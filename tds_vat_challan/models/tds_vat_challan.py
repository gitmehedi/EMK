from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TdsVendorChallan(models.Model):
    _name = 'tds.vat.challan'
    _inherit = ['mail.thread']
    _order = 'date desc'
    _rec_name = 'supplier_id'
    _description = 'TDS Vendor Challan'

    supplier_id = fields.Many2one('res.partner', string="Vendor", track_visibility='onchange')
    operating_unit_id = fields.Many2one('operating.unit', string='Branch', track_visibility='onchange')
    date = fields.Date(string='Date', track_visibility='onchange', help="Creation date.")
    deposit_date = fields.Datetime(string='Deposit Date', readonly=True, track_visibility='onchange')
    deposit_approver = fields.Many2one('res.users', string='Deposit By', readonly=True,
                                       help="who is deposited.", track_visibility='onchange')
    distribute_date = fields.Datetime(string='Distribute Date', readonly=True, track_visibility='onchange')
    distribute_approver = fields.Many2one('res.users', string='Distribute By', readonly=True,
                                          help="who is distributed.", track_visibility='onchange')
    line_ids = fields.One2many('tds.vat.challan.line', 'parent_id', string='Vendor Challan', select=True,
                               track_visibility='onchange')
    total_amount = fields.Float(string='Total', readonly=True, track_visibility='onchange', compute='_compute_amount')

    state = fields.Selection([
        ('draft', "Pending"),
        ('deposited', "Deposited"),
        ('distributed', "Distributed"),
        ('cancel', "Cancel"),
    ], default='draft', track_visibility='onchange')

    ####################################################
    # Business methods
    ####################################################

    @api.multi
    @api.depends('line_ids')
    def _compute_amount(self):
        for rec in self:
            rec.total_amount = sum([line.total_bill for line in rec.line_ids])

    @api.multi
    def action_deposited(self):
        for record in self:
            if record.state not in ('draft'):
                raise UserError(
                    _("Selected record cannot be deposited as they are not in 'Pending' state."))
            for line in record.line_ids:
                line.write({'state': 'deposited', 'challan_provided': line.undistributed_bill})
            res = {
                'state': 'deposited',
                'deposit_approver': record.env.user.id,
                'deposit_date': fields.Datetime.now(),
            }
            record.write(res)
            record.generate_account_journal()

    @api.multi
    def action_distributed(self):
        for record in self:
            if record.state not in ('deposited'):
                raise UserError(
                    _("Selected record cannot be distributed as they are not in 'Deposited' state."))
            for line in record.line_ids:
                line.write({'state': 'distributed', 'undistributed_bill': 0.0})
            res = {
                'state': 'distributed',
                'distribute_approver': record.env.user.id,
                'distribute_date': fields.Datetime.now(),
            }
            record.write(res)

    @api.one
    def action_cancel(self):
        for line in self.line_ids:
            line.acc_move_line_id.write({'is_deposit': False})
            line.write({'state': 'cancel'})
        res = {
            'state': 'cancel',
        }
        self.write(res)

    @api.multi
    def generate_account_journal(self):
        for rec in self:
            date = fields.Date.context_today(self)
            account_conf_pool = self.env['account.config.settings'].search([], order='id desc', limit=1)
            acc_journal_objs = account_conf_pool.tds_vat_transfer_journal_id
            account_move_obj = self.env['account.move']
            account_move_line_obj = self.env['account.move.line'].with_context(check_move_validity=False)
            move_obj = rec._generate_move(acc_journal_objs,account_move_obj,date)
            for line in rec.line_ids:
                self._generate_debit_move_line(line, date, move_obj.id, account_move_line_obj)
            self._generate_credit_move_line(account_conf_pool.tds_vat_transfer_account_id,date,move_obj.id,account_move_line_obj)
            # move_obj.post()
        return True

    def _generate_move(self, journal,account_move_obj,date):
        if not journal.sequence_id:
            raise UserError(_('Configuration Error !'), _('The journal %s does not have a sequence, please specify one.') % journal.name)
        if not journal.sequence_id.active:
            raise UserError(_('Configuration Error !'), _('The sequence of journal %s is deactivated.') % journal.name)

        name = journal.with_context(ir_sequence_date=date).sequence_id.next_by_id()
        account_move_id = False
        if not account_move_id:
            account_move_dict = {
                'name': name,
                'date': date,
                'ref': '',
                'company_id': self.operating_unit_id.partner_id.id,
                'journal_id': journal.id,
                'operating_unit_id': self.operating_unit_id.id,
            }
            account_move = account_move_obj.create(account_move_dict)
        return account_move

    def _generate_credit_move_line(self,tds_vat_transfer_account_id,date,account_move_id,account_move_line_obj):
        account_move_line_credit = {
            'account_id': tds_vat_transfer_account_id.id,
            'credit': self.total_amount,
            'date_maturity': date,
            'debit':  False,
            'name': '/',
            'operating_unit_id':  self.operating_unit_id.id,
            'move_id': account_move_id,
            # 'partner_id': acc_inv_line_obj.partner_id.id,
            # 'analytic_account_id': acc_inv_line_obj.account_analytic_id.id,
        }
        account_move_line_obj.create(account_move_line_credit)
        return True

    def _generate_debit_move_line(self,line,date,account_move_id,account_move_line_obj):
        account_move_line_debit = {
            'account_id': line.acc_move_line_id.account_id.id,
            'analytic_account_id': line.acc_move_line_id.analytic_account_id.id,
            'credit': False,
            'date_maturity': date,
            'debit':  line.total_bill,
            'name': 'challan/'+line.acc_move_line_id.name,
            'operating_unit_id':  self.operating_unit_id.id,
            'move_id': account_move_id,
            # 'partner_id': acc_inv_line_obj.partner_id.id,
        }
        account_move_line_obj.create(account_move_line_debit)
        return True

    ####################################################
    # ORM Overrides methods
    ####################################################

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You cannot delete a record which is not draft state!'))
        return super(TdsVendorChallan, self).unlink()


class TdsVendorChallanLine(models.Model):
    _name = 'tds.vat.challan.line'

    supplier_id = fields.Many2one('res.partner', string="Vendor")
    challan_provided = fields.Float(String='Challan Provided')
    total_bill = fields.Float(String='Total Bill')
    undistributed_bill = fields.Float(String='Undistributed Bill')
    parent_id = fields.Many2one('tds.vat.challan')
    acc_move_line_id = fields.Many2one('account.move.line')
    operating_unit_id = fields.Many2one('operating.unit', string='Branch', track_visibility='onchange')

    state = fields.Selection([
        ('draft', "Draft"),
        ('deposited', "Deposited"),
        ('distributed', "Distributed"),
        ('cancel', "Cancel"),
    ], default='draft', track_visibility='onchange')
