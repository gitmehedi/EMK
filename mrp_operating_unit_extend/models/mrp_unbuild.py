# imports of odoo
from odoo import api, fields, models, _


class MrpUnbuild(models.Model):
    _inherit = 'mrp.unbuild'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=1,
                                        domain=lambda self: [("id", "in", self.env.user.operating_unit_ids.ids)],
                                        default=lambda self: self.env.user.default_operating_unit_id)

    @api.onchange('mo_id')
    def onchange_mo_id(self):
        super(MrpUnbuild, self).onchange_mo_id()
        if self.mo_id:
            self.operating_unit_id = self.mo_id.operating_unit_id

    @api.onchange('product_id')
    def onchange_product_id(self):
        super(MrpUnbuild, self).onchange_product_id()
        if self.mo_id:
            self.operating_unit_id = self.env.user.default_operating_unit_id

    @api.model
    def create(self, vals):
        if vals.get('mo_id', False):
            mo = self.env['mrp.production'].search([('id', '=', vals['mo_id'])])
            vals['operating_unit_id'] = mo.operating_unit_id.id

        if not vals.get('name'):
            ou = self.env['operating.unit'].search([('id', '=', vals['operating_unit_id'])])
            vals['name'] = self.env['ir.sequence'].next_by_code_new('mrp.unbuild', None, ou) or _('New')

        return super(MrpUnbuild, self).create(vals)
