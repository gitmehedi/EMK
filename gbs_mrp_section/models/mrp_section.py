from odoo import models, fields, api

class MrpSection(models.Model):
    _name = 'mrp.section'

    name = fields.Char('Section')
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True, readonly=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)

