# imports of odoo
from odoo import models, fields, api, _


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', default=lambda self: self.env.user.default_operating_unit_id)
