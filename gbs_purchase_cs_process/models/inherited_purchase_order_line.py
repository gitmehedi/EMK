from odoo import fields, models, api


class InheritedPurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    is_cs_processed = fields.Boolean(default=False)

    created_po = fields.Text()
