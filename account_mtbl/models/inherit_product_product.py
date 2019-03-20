from odoo import models, fields, api, _

class ProductProduct(models.Model):
    _inherit = 'product.product'

    parent_id = fields.Many2one(track_visibility='onchange')
    default_code = fields.Char(track_visibility='onchange')
    barcode = fields.Char(track_visibility='onchange')
    lst_price = fields.Float(track_visibility='onchange')
    standard_price = fields.Float(track_visibility='onchange')

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            filters_name = [['name', '=ilike', self.name]]
            name = self.search(filters_name)
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')