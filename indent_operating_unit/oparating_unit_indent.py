from odoo import fields, models, api

class OperatingUnitIndent(models.Model):
    _inherit = 'indent.indent'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)