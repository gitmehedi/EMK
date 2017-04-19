# sprite class

from openerp import models, fields

class LateTime(models.Model):
    _name = 'hr.attendance.absent.time'

    check_in = fields.Datetime(string='Check In')
    check_out = fields.Datetime(string='Check Out')
    duration = fields.Float(string='Hours')

    """ Relational Fields """
    absent_day_id = fields.Many2one("hr.attendance.absent.day", string="Absent Day", required=True, ondelete='cascade')



class TempLateTime(object):

    def __init__(self, check_in=None, check_out=None, duration=None):
        self.check_in = check_in
        self.check_out = check_out
        self.duration = duration
