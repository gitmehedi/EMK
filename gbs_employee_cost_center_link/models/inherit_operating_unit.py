from odoo import fields, models, api


class InheritedOperatingUnit(models.Model):
    _inherit = 'operating.unit'
    _description = 'Inherits Operating Unit to add field cost center required or not'

    cost_center_required = fields.Boolean('Is Cost Center Required', default=False, required=True)
