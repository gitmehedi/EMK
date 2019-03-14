from odoo import api, fields, models, tools, _


class ProductCategory(models.Model):
    _name = "product.uom"
    _inherit = ['product.category', 'mail.thread']