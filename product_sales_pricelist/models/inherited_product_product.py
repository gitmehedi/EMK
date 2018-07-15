from odoo import fields, models


class InheritedProductProduct(models.Model):
    _inherit = 'product.product'

    discount = fields.Float(string='Discount', readonly=True)

