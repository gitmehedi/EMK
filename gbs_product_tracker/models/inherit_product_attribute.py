from odoo import api, fields, models, tools, _


class ProductCategory(models.Model):
    _name = "product.attribute"
    _inherit = ['product.attribute', 'mail.thread']


    name = fields.Char('Name', required=True, translate=True,track_visibility='onchange')
    create_variant = fields.Boolean(default=True, track_visibility='onchange',help="Check this if you want to create multiple variants for this attribute.")
