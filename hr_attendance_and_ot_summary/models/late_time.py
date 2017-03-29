# sprite class

from openerp import models, fields


class LateTime(models.Model):
    _name = 'hr.attendance.late.time'

    check_in = fields.Datetime(string='Check In Time')
    check_out = fields.Datetime(string='Check Out Time')
    duration = fields.Float(string='Hours')

    """ Relational Fields """
    late_day_id = fields.Many2one("hr.attendance.late.day", string="Late Day", required=True)


class TempLateTime(object):

    def __init__(self, check_in=None, check_out=None, duration=None):
        self.check_in = check_in
        self.check_out = check_out
        self.duration = duration