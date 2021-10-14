from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = ['account.invoice', 'ir.needaction_mixin']
    _order = 'number DESC, id desc'

    security_deposit = fields.Float('Security Deposit', track_visibility='onchange', copy=False,
                                    readonly=True, states={'draft': [('readonly', False)]})
    security_deposit_account_id = fields.Many2one('account.account', string='Security Deposit Account',
                                                  default=lambda
                                                      self: self.env.user.company_id.security_deposit_account_id.id,
                                                  required=True, readonly=True, states={'draft': [('readonly', False)]})

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        move_lines = super(AccountInvoice, self).finalize_invoice_move_lines(move_lines)
        if self.security_deposit > 0.0:
            for line in move_lines:
                if line[2]['account_id'] == self.partner_id.property_account_payable_id.id:
                    line[2]['credit'] = line[2]['credit'] - self.security_deposit
            security_deposit_values = self.get_security_deposit_move_data()
            move_lines.append((0, 0, security_deposit_values))
        return move_lines

    def get_security_deposit_move_data(self):
        move_data = {
                'account_id': self.security_deposit_account_id.id,
                'analytic_account_id': self.invoice_line_ids[0].account_analytic_id.id,
                'credit': self.security_deposit,
                'date_maturity': self.date_due,
                'debit': False,
                'invoice_id': self.id,
                'name': 'Security Deposit',
                'partner_id': self.partner_id.id,
                'is_security_deposit': True
            }
        return move_data

    @api.multi
    def action_invoice_open(self):
        res = super(AccountInvoice, self).action_invoice_open()
        if res:
            if self.security_deposit > 0:
                self.create_security_deposit()
        return res

    def create_security_deposit(self):
        security_deposit_data = self.get_security_deposit_data()
        res = self.env['vendor.security.deposit'].create(security_deposit_data)
        return res

    def get_security_deposit_data(self):
        security_deposit_data = {
            'partner_id': self.partner_id.id,
            'amount': self.security_deposit,
            'account_id': self.company_id.security_deposit_account_id.id,
            'date': self.date_invoice,
            'state': 'approve',
            'name': self.number,
            'description': self.invoice_line_ids[0].name or 'Vendor Bill'
        }
        return security_deposit_data

    @api.constrains('security_deposit')
    def _check_security_deposit_amount(self):
        for rec in self:
            if rec.security_deposit < 0:
                raise ValidationError("[Error]Security Deposit can not be less than Zero")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_security_deposit = fields.Boolean(default=False)


