from odoo import api, fields, models,_


class ShipmentProductLine(models.Model):
    _name = 'shipment.product.line'
    _description = 'Shipment Product Line'
    _order = "date_planned desc"

    name = fields.Text(string='Description', required=True)
    product_id = fields.Many2one('product.product', string='Product',
                                 change_default=True, required=True)
    currency_id = fields.Many2one('res.currency', 'Currency')
    date_planned = fields.Datetime(string='Scheduled Date', index=True)
    product_uom = fields.Many2one('product.uom', string='Product Unit of Measure')
    product_received_qty = fields.Float(string='Received Quantity')
    product_qty = fields.Float(string='Quantity')
    price_unit = fields.Float(string='Unit Price')
    shipment_id = fields.Many2one('purchase.shipment', string='Purchase Shipment')


class ShipmentProduct(models.Model):
    _inherit = 'purchase.shipment'

    shipment_product_lines = fields.One2many('shipment.product.line', 'shipment_id', string='Product(s)')