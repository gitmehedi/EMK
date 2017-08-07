from openerp import api, fields, models
from datetime import date

class HREmployee(models.Model):
    _name='hr.excluded.employee'

    employee_name = fields.Char(string="Employee Name")
    acc_number = fields.Integer(string="Account Number")
    department_id = fields.Many2one('hr.department',string='Department')