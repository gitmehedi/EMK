from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    price_history_ids = fields.One2many('product.price.history', 'product_id',
                                        'Product Price History')
