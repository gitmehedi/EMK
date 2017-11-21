from odoo import api, fields, models,_


class ShipmentProductLine(models.Model):
    _name = 'shipment.product.line'
    _description = 'Product'
    _order = "date_planned desc"

    name = fields.Text(string='Description', required=True)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)],
                                 change_default=True, required=True)

    product_qty = fields.Float(string='Quantity')
    product_received_qty = fields.Float(string='Received Quantity')
    price_unit = fields.Float(string='Unit Price')
    currency_id = fields.Many2one('res.currency', 'Currency')
    date_planned = fields.Datetime(string='Scheduled Date', index=True)
    product_uom = fields.Many2one('product.uom', string='Product Unit of Measure')

    shipment_id = fields.Many2one('purchase.shipment', string='Purchase Shipment')

class ShipmentProduct(models.Model):
    _inherit = 'purchase.shipment'

    # po_ids = fields.Many2many('purchase.order', 'po_lc_rel', 'lc_id', 'po_id', string='Purcahse Order')
    shipment_product_lines = fields.One2many('shipment.product.line', 'shipment_id', string='Product(s)')

    @api.onchange('lc_id')
    def po_product_line(self):
        self.shipment_product_lines = []
        vals = []
        for obj in self.lc_id.product_lines:
            vals.append((0, 0, {'product_id': obj.product_id,
                                'name': obj.name,
                                'product_qty': obj.product_qty,
                                'price_unit': obj.price_unit,
                                'currency_id': obj.currency_id,
                                'date_planned': obj.date_planned,
                                'product_uom':obj.product_uom
                                }))
        self.shipment_product_lines = vals