from odoo import models, fields, api, _


class PaymentInstruction(models.Model):
    _inherit = 'payment.instruction'

    agreement_id = fields.Many2one('agreement',string="Agreement",copy=False)


