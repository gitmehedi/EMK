from odoo import api, fields, models,_
from datetime import date

class HrShiftEmployeeBatch(models.Model):
    _name='hr.shift.employee.batch'

    name = fields.Char(string='Batch Name',required=True)
    effective_from = fields.Date(string='Effective Date', required=True ,default=date.today())
    effective_end = fields.Date(string='Effective End Date', required=True)
    shift_id = fields.Many2one("resource.calendar", string="Shift Name", required=True)

    shift_emp_ids=fields.One2many('hr.shifting.history', 'shift_batch_id')
    # employee_ids = fields.One2many('hr.employee', 'hr_employee_group_rel_shift', 'shift_id', 'employee_id', 'Employees')
