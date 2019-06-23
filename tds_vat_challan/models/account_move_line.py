from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    is_deposit = fields.Boolean('Deposit', default=False)
    is_pending = fields.Boolean('Pending', default=False)
    is_paid = fields.Boolean('Paid', default=False)


    def action_do_pending(self):
        for rec in self:
            rec.is_pending = True
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }


    def action_undo_pending(self):
        for rec in self:
            rec.is_pending = False
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

    @api.multi
    def action_account_move_payment(self,records):
        for rec in records:
            if rec.is_pending is True or rec.is_paid is True:
                raise ValidationError(_('Pending/Paid can not open for payment instruction!'))

        res = self.env.ref('tds_vat_challan.tds_vat_move_payment_wizard')

        total_amount = sum([x.credit for x in records])
        result = {
            'name': _('Payment Instruction'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'tds.vat.move.payment.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {'total_amount': total_amount or False,
                        'records': records and records.ids or False,
                        },
        }

        return result