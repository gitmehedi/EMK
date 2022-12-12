from odoo import api, fields, models, _


class AddInvoiceCancelReason(models.TransientModel):
    _name = "add.invoice.reason"

    invoice_cancel_reason = fields.Char(string="Reason", required=True, size=50)

    # For adding the reason of cancel invoice on invoices
    @api.multi
    def cancel_invoice_wizard(self):
        if self.env.context.get('active_model') == 'account.invoice':
            active_model_id = self.env.context.get('active_id')
            invoice_obj = self.env['account.invoice'].search([('id', '=', active_model_id)])
            invoice_obj.write({'invoice_cancel_reason': self.invoice_cancel_reason})
            invoice_obj.action_invoice_cancel()
