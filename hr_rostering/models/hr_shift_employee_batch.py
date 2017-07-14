from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError
from datetime import date,datetime, timedelta

class HrShiftEmployeeBatch(models.Model):
    _name='hr.shift.employee.batch'

    name = fields.Char(string='Batch Name',required=True)
    effective_from = fields.Date(string='Effective Date')
    effective_end = fields.Date(string='Effective End Date')
    shift_id = fields.Many2one("resource.calendar", string="Shift Name")

    shift_emp_ids = fields.One2many('hr.shifting.history', 'shift_batch_id')




