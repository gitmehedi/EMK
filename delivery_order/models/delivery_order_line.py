from odoo import fields, models


class DOProductLineLayer(models.Model):
    _name = 'delivery.order.line'
    _description = 'Delivery Order line'

    product_id = fields.Many2one('product.product', string="Product", readonly=True, ondelete='cascade')
    uom_id = fields.Many2one('product.uom', string="UoM", ondelete='cascade', readonly=True)
    pack_type = fields.Many2one('product.packaging.mode', string="Packing", ondelete='cascade', readonly=True)
    quantity = fields.Float(string="Delivery Qty", required=True, default=1)

    """ Relational Fields """
    parent_id = fields.Many2one('delivery.order', ondelete='cascade')
