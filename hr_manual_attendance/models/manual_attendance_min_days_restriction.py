from openerp import api
from openerp import fields
from openerp import models

class HrManualAttendanceMinDaysRestriction(models.Model):
    _inherit = 'base.config.settings'
    _name = 'hr.manual.attendance.min.days'
    
    min_days_restriction = fields.Integer(string = 'Minimum Days Restriction', size = 30)
    