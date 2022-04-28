from odoo import api, fields, models


class InheritedHrEmployeeOtherDeduction(models.Model):
    _inherit = 'hr.other.deduction'
    _order = 'id DESC'


    type = fields.Selection([
        ('regular', 'Regular'),
        ('ot', 'OT'),
    ], string='Type',default='regular', required=True)



