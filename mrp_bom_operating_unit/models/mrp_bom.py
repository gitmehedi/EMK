# imports of odoo
from odoo import models, fields, api, _


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', default=lambda self: self.env.user.default_operating_unit_id)

    @api.multi
    def action_confirm(self):
        new_name = self.env['ir.sequence'].next_by_code_new('mrp.bom', None, self.operating_unit_id)
        self.write({
            'name': new_name,
            'base_name': new_name,
            'state': 'confirmed'
        })
