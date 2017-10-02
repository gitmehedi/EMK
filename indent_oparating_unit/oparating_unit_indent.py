from odoo import fields, models, api

class OperatingUnitIndent(models.Model):
    _inherit = 'indent.indent'

    oparating_unit_id = fields.Many2one('operating.unit', 'Oparating Unit',required=True, )