from odoo import api, fields, models,_

class EmployeeSequence(models.Model):

    _inherit = "hr.employee"

    emp_sequence = fields.Integer("Employee Sequence")