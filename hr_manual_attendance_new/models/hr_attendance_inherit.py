from openerp import api
from openerp import fields
from openerp import models

class HrAttendanceInherit(models.Model):
    _inherit = ['hr.attendance']
    
    manual_attendance_request =  fields.Boolean(string='Is it from manual attendance request', default=False)    
    check_in = fields.Datetime(string="Check In", required=False)
