# imports of odoo
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    mrp_type_ids = fields.One2many('product.mrp.type', 'product_id', string='Manufacture Types')


class ProdcutMrpType(models.Model):
    _name = 'product.mrp.type'
    _description = 'Operating Unit wise manufacture type of a product'

    product_id = fields.Many2one('product.product', ondelete='cascade')
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit')
    mrp_type = fields.Selection(
        [('conversion', 'Conversion'),
         ('production', 'Production')],
        string='Manufacturing Type', default='production'
    )

    @api.constrains('operating_unit_id')
    def _check_operating_unit_id(self):
        duplicate_operating_units = self.product_id.mrp_type_ids.filtered(
            lambda r: r.operating_unit_id.id == self.operating_unit_id.id
        )
        if len(duplicate_operating_units) > 1:
            raise ValidationError('You can not select same operating unit')
