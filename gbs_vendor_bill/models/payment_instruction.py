from odoo import models, fields, api, _


class PaymentInstruction(models.Model):
    _inherit = 'payment.instruction'

    invoice_id = fields.Many2one('account.invoice',string="Invoice",copy=False)

    @api.multi
    def action_approve(self):
        self.ensure_one()
        if self.invoice_id:
            for line in self.invoice_id.suspend_security().move_id.line_ids:
                if line.account_id.internal_type in ('receivable', 'payable'):
                    if line.amount_residual < 0:
                        val = -1
                    else:
                        val = 1
                    line.write({'amount_residual': ((line.amount_residual) * val) - self.amount})
            self.invoice_id.write({'payment_approver':self.env.user.name})
            self.write({'state': 'approved'})
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }