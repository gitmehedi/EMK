# sprite class

from openerp import models, fields


class AbsentAttendanceDay(models.Model):
    _name = 'hr.absent.attendance.day'

    check_in = fields.Datetime(string='Check In Time')
    check_out = fields.Datetime(string='Check Out Time')
    duration = fields.Float(string='Hours')

    """ Relational Fields """
    absent_day_id = fields.Many2one("hr.absent.day", string="Absent Day", required=False)


class TempAbsentAttendanceDay(object):

    def __init__(self, check_in=None, check_out=None, duration=None):
        self.check_in = check_in
        self.check_out = check_out
        self.duration = duration