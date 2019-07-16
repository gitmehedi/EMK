from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TdsVatChallan(models.Model):
    _name = 'tds.vat.challan'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'challan_date desc'
    _description = 'TDS Vendor Challan'

    name = fields.Char(string='Challan Name',track_visibility='onchange',readonly=True,
                       default=lambda self: self.env.context.get('name'))
    challan_date = fields.Date(string='Challan Date',track_visibility='onchange',required=True,readonly=True,
                               states={'draft': [('readonly', False)]},
                               default=fields.Date.context_today,help="Challan date")
    challan_no = fields.Char(string='Challan No.',track_visibility='onchange',readonly=True,
                             states={'draft': [('readonly', False)]})
    deposited_bank = fields.Char(string='Deposited Bank', track_visibility='onchange', readonly=True,
                                 states={'draft': [('readonly', False)]})
    bank_branch = fields.Char(string='Bank Branch', track_visibility='onchange', readonly=True,
                              states={'draft': [('readonly', False)]})
    line_ids = fields.One2many('tds.vat.challan.line', 'parent_id', string='Vendor Challan', select=True,readonly=True,
                               states={'draft': [('readonly', False)]},
                               track_visibility='onchange')
    note = fields.Text(string='Narration',track_visibility='onchange',readonly=True,
                       states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.context.get('currency_id'))
    total_amount = fields.Float(string='Total', readonly=True, track_visibility='onchange', compute='_compute_amount')
    acc_move_line_ids = fields.Many2many('account.move.line',string='Account Move Lines',
                                         default=lambda self: self.env.context.get('acc_move_line_ids'))

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirmed"),
        ('approved', "Approved"),
        ('cancel', "Cancel"),
    ], default='draft',string="Status", track_visibility='onchange')



    deposit_date = fields.Datetime(string='Deposit Date', readonly=True, track_visibility='onchange')
    deposit_approver = fields.Many2one('res.users', string='Deposit By', readonly=True,
                                       help="who is deposited.", track_visibility='onchange')
    distribute_date = fields.Datetime(string='Distribute Date', readonly=True, track_visibility='onchange')
    distribute_approver = fields.Many2one('res.users', string='Distribute By', readonly=True,
                                          help="who is distributed.", track_visibility='onchange')

    ####################################################
    # Business methods
    ####################################################

    @api.multi
    @api.depends('line_ids')
    def _compute_amount(self):
        for rec in self:
            rec.total_amount = sum([line.total_bill for line in rec.line_ids])

    @api.onchange('acc_move_line_ids')
    def _onchange_acc_move_line_ids(self):
        if self.acc_move_line_ids:
            vals = []
            if len(self.acc_move_line_ids.ids)>1:
                move_line_ids = str(tuple(self.acc_move_line_ids.ids))
            else:
                move_line_ids = "(" + str(self.acc_move_line_ids.id) + ")"
            query = """SELECT 
                       partner_id as supplier,
                       product_id as product,
                       sum(credit) as amount from account_move_line 
                       WHERE id IN %s 
                       GROUP BY partner_id,product_id""" % (move_line_ids)
            self.env.cr.execute(query)
            for acc_move_line_id in self.env.cr.dictfetchall():
                vals.append((0, 0, {'supplier_id': acc_move_line_id['supplier'],
                                    # 'operating_unit_id': acc_move_line_id.operating_unit_id,
                                    'product_id': acc_move_line_id['product'],
                                    'total_bill': acc_move_line_id['amount'],
                                    'currency_id': self.currency_id.id or False,
                                    }))
            self.line_ids = vals



    @api.multi
    def action_confirm(self):
        for record in self:
            if record.state not in ('draft'):
                raise UserError(
                    _("Selected record cannot be confirm as they are not in 'Draft' state."))
            if not record.challan_no or not record.deposited_bank or not record.bank_branch:
                raise UserError(
                    _("Without Challan No/Deposited Bank/Bank Branch record cannot be confirm. Please fill all those."))
            record.line_ids.write({'state': 'confirm'})
            res = {
                'state': 'confirm',
                # 'deposit_approver': record.env.user.id,
                # 'deposit_date': fields.Datetime.now(),
            }
            record.write(res)

    @api.multi
    def action_approve(self):
        for record in self:
            if record.state not in ('confirm'):
                raise UserError(
                    _("Selected record cannot be approve as they are not in 'Deposited' state."))
            record.line_ids.write({'state': 'approved'})
            res = {
                'state': 'approved',
                # 'distribute_approver': record.env.user.id,
                # 'distribute_date': fields.Datetime.now(),
            }
            record.write(res)

    @api.one
    def action_cancel(self):
        self.line_ids.write({'state': 'cancel'})
        self.write({'state': 'cancel'})

    @api.one
    def action_reset_to_draft(self):
        self.line_ids.write({'state': 'cancel'})
        self.write({'state': 'draft'})

    def action_print(self):
        return self.env['report'].get_action(self, 'tds_vat_challan.report_tds_vat_challan')


    ####################################################
    # ORM Overrides methods
    ####################################################

    @api.model
    def create(self, vals):
        if vals['acc_move_line_ids']:
            move_objs = self.env['account.move.line'].search([('id', 'in', [i[2] for i in vals['acc_move_line_ids']][0])])
            move_objs.write({'is_challan':True})
        return super(TdsVatChallan, self).create(vals)

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You cannot delete a record which is not draft state!'))
            if rec.acc_move_line_ids:
                rec.acc_move_line_ids.write({'is_challan': False})
        return super(TdsVatChallan, self).unlink()

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'confirm')]


class TdsVatChallanLine(models.Model):
    _name = 'tds.vat.challan.line'

    supplier_id = fields.Many2one('res.partner', string="Vendor")
    operating_unit_id = fields.Many2one('operating.unit', string='Branch')
    product_id = fields.Many2one('product.product', string='Product')
    type_name = fields.Char(String='Description')
    total_bill = fields.Float(String='Total Bill')
    parent_id = fields.Many2one('tds.vat.challan')
    currency_id = fields.Many2one('res.currency', string='Currency')

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirmed"),
        ('approved', "Approved"),
        ('cancel', "Cancel"),
    ], default='draft', track_visibility='onchange')


# Accounting treatment previous version
    #
    # @api.multi
    # def generate_account_journal(self):
    #     for rec in self:
    #         date = fields.Date.context_today(self)
    #         account_conf_pool = self.env.user.company_id
    #         if not account_conf_pool.tds_vat_transfer_journal_id and not account_conf_pool.tds_vat_transfer_account_id:
    #             raise UserError(
    #                 _(
    #                     "Account Settings are not properly set. Please contact your system administrator for assistance."))
    #         acc_journal_objs = account_conf_pool.tds_vat_transfer_journal_id
    #         account_move_obj = self.env['account.move']
    #         account_move_line_obj = self.env['account.move.line'].with_context(check_move_validity=False)
    #         move_obj = rec._generate_move(acc_journal_objs, account_move_obj, date)
    #         for line in rec.line_ids:
    #             self._generate_debit_move_line(line, date, move_obj.id, account_move_line_obj)
    #         self._generate_credit_move_line(account_conf_pool.tds_vat_transfer_account_id, date, move_obj.id,
    #                                         account_move_line_obj)
    #         move_obj.post()
    #     return True
    #
    # def _generate_move(self, journal, account_move_obj, date):
    #     if not journal.sequence_id:
    #         raise UserError(_('Configuration Error !'),
    #                         _('The journal %s does not have a sequence, please specify one.') % journal.name)
    #     if not journal.sequence_id.active:
    #         raise UserError(_('Configuration Error !'), _('The sequence of journal %s is deactivated.') % journal.name)
    #
    #     name = journal.with_context(ir_sequence_date=date).sequence_id.next_by_id()
    #     account_move_id = False
    #     if not account_move_id:
    #         account_move_dict = {
    #             'name': name,
    #             'date': date,
    #             'ref': '',
    #             'company_id': self.operating_unit_id.company_id.id,
    #             'journal_id': journal.id,
    #             'operating_unit_id': self.operating_unit_id.id,
    #         }
    #         account_move = account_move_obj.create(account_move_dict)
    #     return account_move
    #
    # def _generate_credit_move_line(self, tds_vat_transfer_account_id, date, account_move_id, account_move_line_obj):
    #     account_move_line_credit = {
    #         'account_id': tds_vat_transfer_account_id.id,
    #         'credit': self.total_amount,
    #         'date_maturity': date,
    #         'debit': False,
    #         'name': '/',
    #         'operating_unit_id': self.operating_unit_id.id,
    #         'move_id': account_move_id,
    #     }
    #     account_move_line_obj.create(account_move_line_credit)
    #     return True
    #
    # def _generate_debit_move_line(self, line, date, account_move_id, account_move_line_obj):
    #     account_move_line_debit = {
    #         'account_id': self.acc_move_line_ids[0].account_id.id,
    #         # 'analytic_account_id': line.acc_move_line_id.analytic_account_id.id,
    #         'credit': False,
    #         'date_maturity': date,
    #         'debit': line.total_bill,
    #         'name': 'challan/' + self.acc_move_line_ids[0].name,
    #         'operating_unit_id': self.operating_unit_id.id,
    #         'move_id': account_move_id,
    #         # 'partner_id': acc_inv_line_obj.partner_id.id,
    #     }
    #     account_move_line_obj.create(account_move_line_debit)
    #     return True
