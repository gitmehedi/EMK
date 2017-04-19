# sprite class

from openerp import models, fields

class AbsentDay(models.Model):

    _name = 'hr.attendance.absent.day'

    date = fields.Date(string='Absent Date')

    schedule_time_start = fields.Datetime(string='Duty Start')
    schedule_time_end = fields.Datetime(string='Duty End')
    ot_time_start = fields.Datetime(string='OT Start')
    ot_time_end = fields.Datetime(string='OT End')

    schedule_working_hours = fields.Float(string='Duty Hours')

    working_hours = fields.Float(string='Present Hours')

    """" Relational Fields """
    attendance_day_list = fields.One2many('hr.attendance.absent.time', 'absent_day_id', string='Employee Attendance')
    att_summary_line_id = fields.Many2one("hr.attendance.summary.line", string="Absent Summary", required=True, ondelete='cascade')

class TempAbsentDay(object):

    def __init__(self, date=None, schedule_time_start=None, schedule_time_end=None,ot_time_start=None,ot_time_end=None,
                 schedule_working_hours=None,working_hours=None,attendance_day_list=None):
        self.date = date
        self.schedule_time_start = schedule_time_start
        self.schedule_time_end = schedule_time_end
        self.ot_time_start = ot_time_start
        self.ot_time_end = ot_time_end
        self.schedule_working_hours = schedule_working_hours
        self.working_hours = working_hours
        if attendance_day_list is None:
            self.attendance_day_list = []
        else:
            self.attendance_day_list = attendance_day_list