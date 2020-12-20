# imports of odoo
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', default=lambda self: self.env.user.default_operating_unit_id)

    @api.multi
    def action_confirm(self):
        bom = self.env['mrp.bom'].search([('product_id', '=', self.product_id.id),
                                          ('operating_unit_id', '=', self.operating_unit_id.id),
                                          ('active', '=', True)])
        if bom.ids:
            raise Warning(_('Already BOM exists for "%s" product variant of "%s" operating unit.\n'
                            'You are only allowed to create new version of "%s" product variant.')
                          % (self.product_id.name, self.operating_unit_id.name, self.product_id.name))

        new_name = self.env['ir.sequence'].next_by_code_new('mrp.bom', None, self.operating_unit_id)
        self.write({
            'name': new_name,
            'base_name': new_name,
            'state': 'confirmed'
        })
