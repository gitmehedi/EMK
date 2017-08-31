from openerp import api, fields, models


class InheritedPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    order_quantity_ids = fields.One2many('purchase.order.quantity', 'purchase_order_id', string="Order Quantity")

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        res = super(InheritedPurchaseOrder, self).wkf_confirm_order(cr, uid, ids, context=context)
        for record in self.browse(cr, uid, ids, context=context):
            for rec in record.order_line:
                for ins in rec.product_id.product_variant_ids:
                    record.order_quantity_ids.create({
                        'product_id': ins.id,
                        'quantity': 0,
                        'purchase_order_id': record.id,
                    })

        return True


class PurchaseOrderQuantity(models.Model):
    _name = 'purchase.order.quantity'

    product_id = fields.Many2one('product.product', string="Product", required=True)
    quantity = fields.Float(string="Quantity", required=True)

    purchase_order_id = fields.Many2one('purchase.order', string='Order')
