# imports of odoo
from odoo import models, fields, api, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    mrp_type = fields.Selection(
        [('conversion', 'Conversion'),
         ('production', 'Production')],
        string='Manufacturing Type', default='production'
    )

    @api.onchange('product_id', 'operating_unit_id')
    def _onchange_product_id(self):
        product_mrp_type = self.product_id.mrp_type_ids.filtered(
            lambda t: t.operating_unit_id.id == self.operating_unit_id.id
        )
        self.mrp_type = product_mrp_type.mrp_type or self.mrp_type
