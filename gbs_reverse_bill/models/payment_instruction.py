from odoo import models, fields, api, _


class PaymentInstruction(models.Model):
    _inherit = 'payment.instruction'

    @api.multi
    def action_invoice_reverse(self):
        if self.invoice_id:
            for line in self.invoice_id.suspend_security().move_id.line_ids:
                if line.account_id.internal_type in ('receivable', 'payable'):
                    line.write({'amount_residual': 0.0})
        return True