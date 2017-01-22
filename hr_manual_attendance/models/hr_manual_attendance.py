from openerp import api
from openerp import fields
from openerp import models


class HrManualAttendance(models.Model):
    _name = 'hr.manual.attendance'
    # _inherit = ['mail.thread']

    #Fields of Model    
    name = fields.Char(string='Employee Name', required = True, size = 30)
    employee_id = fields.Integer(size=30, string="Employee ID")    
    reason = fields.Text(string='Reason')
    is_it_official = fields.Boolean(string='Is it official', default=False)
    state = fields.Char(string='State', size = 30)        
    department_name = fields.Char(string='Department Name', size = 30)    
    check_in_time_full_day = fields.Date(string = 'Check In time')
    check_out_time_full_day = fields.Date(string = 'Check out time fULL')    
    check_in_time_sign_in = fields.Date(string = 'Check In time')
    check_in_time_sign_out = fields.Date(string = 'Check Out time')
    sign_type = fields.Selection([
        ('full_day', 'Full Day'),
        ('sign_in', 'Sign In'),
        ('sign_out', 'Sign Out')
        ], string = 'Sign Type')
    
    
    

    
    
    
    
    
    
    
    


