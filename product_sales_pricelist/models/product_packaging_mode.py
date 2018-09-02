from odoo import fields, models,api
from odoo.exceptions import UserError, ValidationError, Warning


class ProductPackagingMode(models.Model):
    _name = 'product.packaging.mode'
    _description = "Product Package Mode"
    _rec_name = 'packaging_mode'
    _order = 'sequence asc'

    packaging_mode = fields.Char(string='Packaging Mode', required=True)
    is_jar_bill_included = fields.Boolean(string='Is Jar Bill Included?')
    uom_id = fields.Many2one('product.uom', string='UoM')
    sequence = fields.Integer('Sequence')

    @api.constrains('packaging_mode')
    def _check_unique_packaging_mode(self):
        name = self.env['product.packaging.mode'].search([('packaging_mode', '=', self.packaging_mode)])
        if len(name) > 1:
            raise ValidationError("Packaging Mode's name must be unique!")