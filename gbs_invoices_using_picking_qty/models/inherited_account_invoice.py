from odoo import fields, models, api


class InheritedAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    from_po_form = fields.Boolean(default=False)
