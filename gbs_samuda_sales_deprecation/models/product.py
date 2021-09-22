# imports of odoo
from odoo import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_deprecated = fields.Boolean(string="Deprecated")
