from odoo import models, fields, api

class FineshProduct(models.Model):
    _name = 'finish.product.line'

    product_id = fields.Many2one('product.template','Product Name')
    daily_pro_id = fields.Many2one('daily.production','Daily Production')
    qty = fields.Float('Quantity')
    date = fields.Date('Date')
    uom_id = fields.Many2one('product.uom','UOM')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('approved', 'Approved'),
        ('reset', 'Reset To Draft'),
    ], string='Status', default='draft')
