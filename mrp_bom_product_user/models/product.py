# imports of odoo
from odoo import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = "product.product"

    manufacture_ok = fields.Boolean(string="Can be Manufactured", default=False,
                                    help="This is used for Allowing Products in User Account")
