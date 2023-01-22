from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_move_create(self):
        res = super(AccountInvoice, self.sudo()).action_move_create()
        if res:
            for inv in self:
                account_move = self.env['account.move'].search([('id', '=', inv.move_id.id)])
                for line in account_move.line_ids:
                    if line.advance_id:
                        line_ou = line.advance_id.operating_unit_id.id
                        line.write({'operating_unit_id': line_ou})
        return res

