from odoo import models, fields ,api

class HrEmployeeSequenceInherit(models.Model):
    _inherit = ['hr.employee']
        
    employee_sequence = fields.Integer(size=20, string='Employee Sequence')