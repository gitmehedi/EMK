from odoo import fields, models, api


class DOProductLineLayer(models.Model):
    _name = 'delivery.order.line'
    _description = 'Delivery Order line'

    product_id = fields.Many2one('product.product', string="Product", readonly=True, ondelete='cascade')
    uom_id = fields.Many2one('product.uom', string="UoM", ondelete='cascade', readonly=True)
    pack_type = fields.Many2one('product.packaging.mode', string="Packing", ondelete='cascade', readonly=True)
    quantity = fields.Float(string="Ordered Qty", required=True, default=1)

    qty_delivered = fields.Float('Delivered', compute='_get_delivered_qty',store = True)
    date_done = fields.Datetime('Date of Transfer', copy=False, readonly=True, help="Completion Date of Transfer")

    """ Relational Fields """
    parent_id = fields.Many2one('delivery.order', ondelete='cascade')

    delivery_qty = fields.Float(string='Delivery Qty')

    @api.one
    @api.depends('parent_id.sale_order_id.order_line.qty_delivered')
    def _get_delivered_qty(self):
        so_id = self.env['sale.order'].search([('id', '=', self.parent_id.sale_order_id.id)])
        quantity = so_id.order_line.filtered(lambda x: x.product_id.id == self.product_id.id).qty_delivered
        self.qty_delivered = quantity

