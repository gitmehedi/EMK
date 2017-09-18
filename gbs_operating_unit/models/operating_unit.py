from odoo import api, fields, models,_
from odoo.exceptions import UserError, AccessError, ValidationError

class GbsOperatingUnit(models.Model):
    _inherit = 'operating.unit'

    operating_unit_sequence = fields.Integer(string="Sequence")