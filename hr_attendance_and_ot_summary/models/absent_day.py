# sprite class

from openerp import models, fields

class AbsentDay(models.Model):

    _name = 'hr.absent.day'

    date = fields.Date(string='Duty Date')

    scheduleTimeStart = fields.Datetime(string='Duty Time Start')
    scheduleTimeEnd = fields.Datetime(string='Duty Time End')
    otTimeStart = fields.Datetime(string='OT Time Start')
    otTimeEnd = fields.Datetime(string='OT Time End')

    scheduleWorkingHours = fields.Float(string='Duty Hours')

    workingHours = fields.Float(string='Working Hours')

    """" Relational Fields """
    attendance_day_list = fields.One2many('hr.absent.attendance.day', 'absent_day_id', string='Employee Attendance', copy=True)
    absent_summary_id = fields.Many2one("hr.absent.summary", string="Absent Summary", required=False)

class TempAbsentDay(object):

    def __init__(self, date=None, scheduleTimeStart=None, scheduleTimeEnd=None,otTimeStart=None,otTimeEnd=None,scheduleWorkingHours=None,workingHours=None,attendance_day_list=None):
        self.date = date
        self.scheduleTimeStart = scheduleTimeStart
        self.scheduleTimeEnd = scheduleTimeEnd
        self.otTimeStart = otTimeStart
        self.otTimeEnd = otTimeEnd
        self.scheduleWorkingHours = scheduleWorkingHours
        self.workingHours = workingHours
        self.attendance_day_list = attendance_day_list