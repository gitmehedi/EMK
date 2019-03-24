from odoo import api, fields, models,_


class ProductCategory(models.Model):
    _inherit = 'product.category'

    is_backdateable = fields.Boolean(string='Is Backdate-able', default=False)