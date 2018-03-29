from odoo import api, fields, models,_

class EmployeeSequence(models.Model):

    _inherit = "hr.employee"

    employee_sequence = fields.Integer("Employee Sequence")