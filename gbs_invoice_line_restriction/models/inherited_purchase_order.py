from odoo import fields, models, api


class InheritedPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def action_view_invoice(self):
        result = super(InheritedPurchaseOrder, self).action_view_invoice()
        result['context']['default_from_po_form'] = True
        return result
