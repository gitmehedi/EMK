from odoo import models, fields, api, _


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = ['account.invoice', 'ir.needaction_mixin']
    _order = 'number DESC, id desc'

    @api.multi
    def action_move_create(self):
        res = super(AccountInvoice, self.sudo()).action_move_create()
        if res:
            for inv in self:
                account_move = self.env['account.move'].search([('id', '=', inv.move_id.id)])
                for line in account_move.line_ids:
                    if line.is_security_deposit:
                        if self.env.user.company_id.security_deposit_operating_unit_id:
                            line_ou = self.env.user.company_id.security_deposit_operating_unit_id.id
                        else:
                            line_ou = self.operating_unit_id.id
                        line.write({'operating_unit_id': line_ou})
        return res

    def create_security_deposit(self):
        res = super(AccountInvoice, self).create_security_deposit()
        res.write({'operating_unit_id': self.env.user.company_id.security_deposit_operating_unit_id.id})
        return res
