from odoo import api, fields, models


class InheritedHrEmployeeArrear(models.Model):
    _inherit = 'hr.payroll.arrear'
    _order = 'id DESC'


    type = fields.Selection([
        ('regular', 'Regular'),
        ('ot', 'OT'),
    ], string='Type',default='regular', required=True)


