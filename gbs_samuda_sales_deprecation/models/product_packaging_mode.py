from odoo import fields, models, api, _


class ProductPackagingMode(models.Model):
    _inherit = 'product.packaging.mode'

    is_deprecated = fields.Boolean(string="Deprecated")
