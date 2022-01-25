from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class VendorAdvance(models.Model):
    _name = "vendor.advance"
    _description = 'Vendor Advance'
    _order = 'id desc'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char(string='Name', default='/', required=True, copy=False, track_visibility='onchange')
    description = fields.Char(string='Narration', readonly=True, states={'draft': [('readonly', False)]},
                              track_visibility='onchange')
    date = fields.Date(string='Date ', default=fields.Date.today(), required=True, track_visibility='onchange',
                       readonly=True, states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', string='Vendor', ondelete='restrict', required=True,
                                 domain=[('parent_id', '=', False), ('supplier', '=', True)],
                                 readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit',
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid),
                                        readonly=True, required=True,
                                        states={'draft': [('readonly', False)]})
    advance_amount = fields.Float(string="Approved Advance", required=True, readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  track_visibility='onchange', help="Finally granted advance amount.")
    adjusted_amount = fields.Float(string="Adjusted Amount", track_visibility='onchange', copy=False,
                                   help="Total amount which are already adjusted in bill.")
    outstanding_amount = fields.Float(string="Outstanding Amount", compute="_compute_outstanding_amount", copy=False,
                                      track_visibility='onchange', help="Remaining Amount to adjustment.", store=True)
    security_deposit = fields.Float(string="Security Deposit", default=0.0, track_visibility='onchange',
                                    readonly=True, states={'draft': [('readonly', False)]}, help="Security Deposit.")
    tds_amount = fields.Float('TDS Amount', readonly=True, copy=False, states={'draft': [('readonly', False)]})
    vat_amount = fields.Float('VAT Amount', readonly=True, copy=False, states={'draft': [('readonly', False)]})
    payable_to_supplier = fields.Float('Vendor Payable', readonly=True, store=True, copy=False,
                                       compute="_compute_payable_to_supplier", digits=(16, 2),
                                       help="This is the advance amount after deducting security deposit, Vat and Tax")
    vat_account_id = fields.Many2one('account.account', string="VAT Account", readonly=True,
                                     track_visibility='onchange', states={'draft': [('readonly', False)]})
    tds_account_id = fields.Many2one('account.account', string="TDS Account", readonly=True,
                                     track_visibility='onchange', states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    company_id = fields.Many2one('res.company', string='Company', readonly=True, track_visibility='onchange',
                                 states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env.user.company_id.id)
    journal_id = fields.Many2one('account.journal', string='Account Journal', copy=False,
                                 readonly=True, states={'draft': [('readonly', False)]})
    move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True, copy=False)
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Waiting for Approval"),
        ('approve', 'Open'),
        ('done', "Closed"),
        ('cancel', "Canceled")], default='draft', string="Status", copy=False, track_visibility='onchange')

    @api.depends('advance_amount', 'security_deposit', 'vat_amount', 'tds_amount')
    def _compute_payable_to_supplier(self):
        for rec in self:
            rec.payable_to_supplier = rec.advance_amount - (rec.security_deposit + rec.vat_amount + rec.tds_amount)

    @api.depends('adjusted_amount', 'state', 'advance_amount')
    def _compute_outstanding_amount(self):
        for rec in self:
            if rec.state not in ('draft', 'cancel'):
                rec.outstanding_amount = rec.advance_amount - rec.adjusted_amount
            else:
                rec.outstanding_amount = 0.0

    @api.constrains('date')
    def _check_date(self):
        if self.date > fields.Date.today():
            raise ValidationError("Date cannot be greater than Current Date!")

    @api.constrains('advance_amount')
    def _check_advance_amount(self):
        if self.advance_amount <= 0:
            raise ValidationError("Please Check Your Advance Amount!! \n Amount Never Take Negative or Zero Value!")

    @api.constrains('security_deposit')
    def _check_security_deposit(self):
        if self.security_deposit < 0:
            raise ValidationError(_("[Validation Error] Security Deposit can not be negative value!"))

    @api.constrains('vat_amount')
    def _check_vat_amount(self):
        if self.vat_amount < 0:
            raise ValidationError(_("[Validation Error] VAT Amount can not be negative value!"))
        if self.vat_amount > 0 and not self.vat_account_id:
            raise ValidationError(_("Please give VAT Account!"))

    @api.constrains('tds_amount')
    def _check_tds_amount(self):
        if self.tds_amount < 0:
            raise ValidationError(_("[Validation Error] TDS Amount can not be negative value!"))
        if self.tds_amount > 0 and not self.tds_account_id:
            raise ValidationError(_("Please give TDS Account!"))

    @api.one
    def action_confirm(self):
        if self.state == 'draft':
            if (self.security_deposit + self.vat_amount + self.tds_amount) > self.advance_amount:
                raise ValidationError(
                    _("[Validation Error] Summation of Security Deposit, VAT and TDS"
                      " cannot be greater than approved advance!"))
            name = self.env['ir.sequence'].next_by_code('vendor.advance') or ''
            self.write({
                'state': 'confirm',
                'name': name
            })

    @api.one
    def action_validate(self):
        if self.state == 'confirm':
            # if self.security_deposit > 0:
            #     self.create_security_deposit()
            move = self._generate_move()
            if move:
                self.write({
                    'state': 'approve',
                    'move_id': move.id
                })

    @api.multi
    def action_draft(self):
        if self.state == 'cancel':
            self.write({'state': 'draft'})

    @api.multi
    def action_cancel(self):
        if self.state == 'approve':
            self.write({'state': 'cancel'})

    def _generate_move(self):
        line_ids = []

        # debit part
        debit_aml_dict = self._generate_debit_move_line(self.partner_id.property_account_payable_id.id,
                                                        self.advance_amount, self.description)
        line_ids.append([0, 0, debit_aml_dict])

        # credit part
        # bank
        bank_aml_dict = self._generate_credit_move_line(self.journal_id.default_debit_account_id.id, self.payable_to_supplier, self.description)
        line_ids.append([0, 0, bank_aml_dict])
        # vat
        if self.vat_amount > 0:
            vat_aml_dict = self._generate_credit_move_line(self.vat_account_id.id, self.vat_amount, self.description)
            line_ids.append([0, 0, vat_aml_dict])
        # tds
        if self.tds_amount > 0:
            tds_aml_dict = self._generate_credit_move_line(self.tds_account_id.id, self.tds_amount, self.description)
            line_ids.append([0, 0, tds_aml_dict])

        move_dict = {
            'name': self.name,
            'date': self.date if self.date else fields.date.today(),
            'journal_id': self.journal_id.id,
            'operating_unit_id': self.operating_unit_id.id,
            'company_id': self.company_id.id,
            'currency_id': self.currency_id.id,
            'line_ids': line_ids
        }

        move = self.env['account.move'].create(move_dict)
        move.sudo().post()

        return move

    def _generate_credit_move_line(self, account_id, credit, description):
        return {
            'account_id': account_id,
            'date_maturity': self.date,
            'amount_currency': 0,
            'credit': credit,
            'debit':  False,
            'ref': self.name,
            'name': description or 'Vendor Advance',
            'operating_unit_id':  self.operating_unit_id.id,
            'partner_id': self.partner_id.id
        }

    def _generate_debit_move_line(self, account_id, debit, description):
        return {
            'account_id': account_id,
            'date_maturity': self.date,
            'amount_currency': 0,
            'credit': False,
            'debit': debit,
            'ref': self.name,
            'name': description or 'Vendor Advance',
            'operating_unit_id': self.operating_unit_id.id,
            'partner_id': self.partner_id.id
        }

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You cannot delete a record which is not draft state!'))
        return super(VendorAdvance, self).unlink()
