# sprite class

from openerp import models, fields

class AttendanceSummaryLine(models.Model):
    _name = 'hr.attendance.summary.line'

    salary_days = fields.Integer(string='Salary Days', required=True)    #
    present_days = fields.Integer(string='Present Days', required=True)
    late_days_overwrite = fields.Integer(string='Late Days Overwrite')
    leave_days = fields.Integer(string='Leave Days')
    late_hrs = fields.Float(string='Late Hours')
    schedule_ot_hrs = fields.Float(string='Schedule OT Hrs')
    cal_ot_hrs = fields.Float(string='Cal OT Hrs')

    """" Relational Fields """
    att_summary_id = fields.Many2one("hr.attendance.summary", string="Summary", required=True)
    employee_id = fields.Many2one("hr.employee", string='Employee Name', required=True)

    absent_days = fields.One2many('hr.attendance.absent.day', 'att_summary_line_id', string='Absent Days', copy=True)
    late_days = fields.One2many('hr.attendance.late.day', 'att_summary_line_id', string='Late Days', copy=True)
    weekend_days = fields.One2many('hr.attendance.weekend.day', 'att_summary_line_id', string='Weekend Days', copy=True)


class TempAttendanceSummaryLine(object):

    def __init__(self, absent_days=0, ot_hours=0, employee_id=0, absent_day_list=None):
        self.absent_days = absent_days
        self.ot_hours = ot_hours
        self.employee_id = employee_id
        if absent_day_list is None:
            self.absent_day_list = []
        else:
            self.absent_day_list = absent_day_list