from openerp import api
from openerp import fields
from openerp import models
from duplicity.tempdir import default


class HrManualAttendance(models.Model):
    _name = 'hr.manual.attendance'
    _inherit = ['mail.thread']

    #Fields of Model    
    name = fields.Char(size = 30)
    reason = fields.Text(string='Reason')
    is_it_official = fields.Boolean(string='Is it official', default=False)
    state = fields.Char(string='State', size = 30, default = 'draft')        
    department_name = fields.Char(string='Department Name', size = 30)    
    check_in_time_full_day = fields.Date(string = 'Check In time for full day')
    check_out_time_full_day = fields.Date(string = 'Check out time for full day')    
    check_in_time_sign_in = fields.Date(string = 'Check In time for Sign In')
    check_in_time_sign_out = fields.Date(string = 'Check Out time for Sign Out')
    sign_type = fields.Selection([
        ('full_day', 'Full Day'),
        ('sign_in', 'Sign In'),
        ('sign_out', 'Sign Out')
        ], string = 'Sign Type')
    
    employee_id = fields.Many2one('hr.employee', string="Employee Name", required = True)

    
    
    

    
    
    
    
    
    
    
    


