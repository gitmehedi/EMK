from odoo import fields, models

class ProductPackagingMode(models.Model):
    _name = 'product.packaging.mode'
    _description = "Product Package Mode"
    _rec_name = 'packaging_mode'

    packaging_mode = fields.Char(string='Packaging Mode', required=True)
    is_jar_bill_included = fields.Boolean(string='Is Jar Bill Included?')
    uom_id = fields.Many2one('product.uom',string='UoM')

