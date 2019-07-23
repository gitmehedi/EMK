from openerp import api, fields, models


class InheritedPurchaseOrderLine(models.Model):
    _inherit = 'pos.order'

    def _amount_line_tax(self, cr, uid, line, context=None):
        return line.price_subtotal_incl - line.price_subtotal
