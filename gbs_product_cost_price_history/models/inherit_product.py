from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    cost_price_history_ids = fields.One2many('product.cost.price.history', 'product_id',
                                        'Product Cost Price History')
