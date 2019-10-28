from odoo import models, fields, api, _


class PaymentInstruction(models.Model):
    _inherit = 'payment.instruction'

    invoice_id = fields.Many2one('account.invoice',string="Vendor Bill",copy=False)

    @api.multi
    def action_reject(self):
        if self.state == 'draft':
            if self.invoice_id:
                self.invoice_id.write({'payment_approver': self.env.user.name})
            return super(PaymentInstruction, self).action_reject()

    @api.multi
    def action_reset(self):
        if self.state == 'cancel':
            if self.invoice_id:
                self.invoice_id.write({'payment_approver': self.env.user.name})
            return super(PaymentInstruction, self).action_reset()

