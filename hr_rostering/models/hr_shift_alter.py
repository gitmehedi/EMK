from openerp import api,fields,models
from openerp.exceptions import ValidationError,Warning
from datetime import date
import datetime


class HRShiftAlter(models.Model):
    _name = 'hr.shift.alter'
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee', string="Employee", required = True)
    alter_date = fields.Date(string = 'Alter Date')
    alter_time_start = fields.Datetime(string = 'Alter Time Start')
    alter_time_end = fields.Datetime(string = 'Alter Time End')
    ot_time_start = fields.Datetime(string = 'Over Time Start')
    ot_time_end = fields.Datetime(string = 'Over Time End')
    ot_included = fields.Boolean(string='Is OT included')

    
    
    


    
    