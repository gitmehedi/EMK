# sprite class

from openerp import models, fields

class AbsentAttendanceDay(models.Model):
    _name = 'hr.absent.summary'
    
    
    absent_days = fields.Integer(string='Absent Days')
    updated_absent_days = fields.Integer(string='Update Absent Days')
    ot_hours = fields.Float(string='Calculated OT Hours')
    updated_ot_hours = fields.Float(string='Update OT Hours')

    """" Relational Fields """
    employee_id = fields.Many2one("hr.employee", string='Employee Name', required=True)

    absent_summary_list = fields.One2many('hr.absent.day', 'absent_summary_id', string='Absent Summary', copy=True)

    #@Todo Updated by date range id
    # date_from = fields.Date(required=True)
    # date_to = fields.Date(required=True)

class TempAbsentSummary(object):

    def __init__(self, absent_days=0, ot_hours=0, employee_id=0, absent_day_list=None):
        self.absent_days = absent_days
        self.ot_hours = ot_hours
        self.employee_id = employee_id
        if absent_day_list is None:
            self.absent_day_list = []
        else:
            self.absent_day_list = absent_day_list