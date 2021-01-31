# imports of odoo
from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    manufacture_ok = fields.Boolean(string="Can be Manufactured", default=False,
                                    help="Only Checked Product Varianst(s) are available on User Account page "
                                         "for Selecting Product Varianst(s) of Varianst(s) wise "
                                         "BOM & Manufacturing access permission.")
