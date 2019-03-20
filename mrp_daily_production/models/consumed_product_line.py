from odoo import models, fields, api

class ConsumedProduct(models.Model):
    _name = 'consumed.product.line'


    product_id = fields.Many2one('product.product', 'Product Name')
    con_product_qty = fields.Float('Quantity')
    daily_pro_id = fields.Many2one('daily.production', 'Daily Production')
    consumed_product_date = fields.Date('Date')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('approved', 'Approved'),
        ('reset', 'Reset To Draft'),
    ], string='Status', default='draft')

