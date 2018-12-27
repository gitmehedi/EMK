from odoo import api, fields, models,_


class ProductCategory(models.Model):
    _inherit = 'product.category'

    is_consumable = fields.Boolean(string='Is Consumable', default=False)