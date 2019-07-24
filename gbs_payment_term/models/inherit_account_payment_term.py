from odoo import models, fields, api


class InheritAccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    terms_type = fields.Selection([
        ('local', 'Local'),
        ('foreign', 'Foreign'),
    ], string='Terms Type', default='local')

    terms_condition = fields.Text(string='Terms & Conditions', required=True)
