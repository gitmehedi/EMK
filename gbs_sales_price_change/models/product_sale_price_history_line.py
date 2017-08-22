from odoo import api, fields, models
from datetime import date

class ProductSalePriceHistiryLine(models.Model):
    _name = 'product.sale.history.line'
    _description = "Sale Price History"
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', string="Product", required=True, domain=[('sale_ok', '=', True)],readonly=True)
    list_price = fields.Float(string='Old Price', readonly=True)
    new_price = fields.Float(string='New Price', required=True,readonly=True)
    approve_price_date = fields.Date(string='Approved Date',readonly=True)
    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True)
