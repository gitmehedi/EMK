from odoo import models, fields, api, _


class PaymentInstruction(models.Model):
    _inherit = 'payment.instruction'

    invoice_id = fields.Many2one('account.invoice',string="Invoice",copy=False)