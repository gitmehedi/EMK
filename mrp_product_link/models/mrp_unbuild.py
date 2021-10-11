# imports of odoo
from odoo import api, fields, models, _


class MrpUnbuild(models.Model):
    _inherit = 'mrp.unbuild'

    mrp_type = fields.Selection(
        [('conversion', 'Conversion'),
         ('production', 'Production')],
        string='Manufacturing Type', default='production'
    )

    @api.onchange('mo_id')
    def onchange_mo_id(self):
        super(MrpUnbuild, self).onchange_mo_id()
        if self.mo_id:
            self.mrp_type = self.mo_id.mrp_type

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):
        super(MrpUnbuild, self)._onchange_operating_unit_id()
        product_mrp_type = self.product_id.mrp_type_ids.filtered(
            lambda t: t.operating_unit_id.id == self.operating_unit_id.id
        )
        self.mrp_type = product_mrp_type.mrp_type or self.mrp_type

    @api.onchange('product_id')
    def onchange_product_id(self):
        super(MrpUnbuild, self).onchange_product_id()
        product_mrp_type = self.product_id.mrp_type_ids.filtered(
            lambda t: t.operating_unit_id.id == self.operating_unit_id.id
        )
        self.mrp_type = product_mrp_type.mrp_type or self.mrp_type
