# import of odoo
from odoo import api, fields, models, _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.multi
    def remove_move_reconcile(self):
        res = super(AccountMoveLine, self).remove_move_reconcile()
        for rec in self:
            # for adjusted amount of vendor advance
            vendor_advance = self.env['vendor.advance'].search([('move_id', '=', rec.move_id.id)])
            if rec.user_type_id.type == 'payable' and rec.debit > 0 and vendor_advance:
                adjusted_amount = rec.debit - rec.amount_residual
                if vendor_advance.state == 'done':
                    vendor_advance.write({'adjusted_amount': adjusted_amount, 'state': 'approve'})
                else:
                    vendor_advance.write({'adjusted_amount': adjusted_amount})

        return res
