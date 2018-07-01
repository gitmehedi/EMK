from odoo import api, fields, models

class SalesDeliveryGoods(models.Model):
    _name = 'sales.delivery.goods'
    _description = 'Sales Delivery Goods'
    _rec_name = 'vehicle_no'

    transport_details = fields.Selection([
        ('owned', 'Owned'),
        ('hired', 'Hired'),
    ], string='Type', required=True)

    transport_name = fields.Char(size=100, string='Transport Details', required=True)
    vehicle_no = fields.Char(size=100, string='Vehicle No.', required=True)
    driver_no = fields.Char(size=100, string='Driver Name', required=True)
    driver_mob = fields.Char(size=100, string='Driver Mob.', required=True)
    product_id = fields.Many2one('product.product', domain=[('sale_ok', '=', True)], string="Product Details", required=False)
    qty = fields.Integer(size=100, string='Qty. (MT)', required=False)







