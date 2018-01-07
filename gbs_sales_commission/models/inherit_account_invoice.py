from odoo import fields,models


class InheritAccountInvoice(models.Model):
    _inherit='account.invoice'

    is_commission_generated = fields.Boolean(string='Commission Generated', default=False)
