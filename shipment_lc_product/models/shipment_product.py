from odoo import api, fields, models,_


class ShipmentProductLine(models.Model):
    _name = 'shipment.product.line'
    _description = 'Product'
    _order = "date_planned desc"

    name = fields.Text(string='Description', required=True)
    lc_pro_line_id = fields.Integer(string='LC Line ID')
    product_id = fields.Many2one('product.product', string='Product',
                                 change_default=True, required=True)
    lc_product_qty = fields.Float(string='LC Quantity')
    currency_id = fields.Many2one('res.currency', 'Currency')
    date_planned = fields.Datetime(string='Scheduled Date', index=True)
    product_uom = fields.Many2one('product.uom', string='Product Unit of Measure')
    product_received_qty = fields.Float(string='Received Quantity')
    product_qty = fields.Float(string='Quantity',compute = '_compute_quantity',store=True)
    # price_unit = fields.Float(string='Unit Price')
    shipment_id = fields.Many2one('purchase.shipment', string='Purchase Shipment')

    @api.multi
    def _compute_quantity(self):
        for shipment in self:
            shipment.product_qty = shipment.lc_product_qty - shipment.product_received_qty

class ShipmentProduct(models.Model):
    _inherit = 'purchase.shipment'

    shipment_product_lines = fields.One2many('shipment.product.line', 'shipment_id', string='Product(s)')

    @api.onchange('lc_id')
    def po_product_line(self):
        self.shipment_product_lines = []
        vals = []
        for obj in self.lc_id.product_lines:
            if obj.product_received_qty<obj.product_qty:
                vals.append((0, 0, {'product_id': obj.product_id,
                                'lc_pro_line_id': obj.id,
                                'name': obj.name,
                                'lc_product_qty': obj.product_qty,
                                'currency_id': obj.currency_id,
                                'date_planned': obj.date_planned,
                                'product_uom':obj.product_uom,
                                'product_received_qty':obj.product_received_qty
                                }))
        self.shipment_product_lines = vals