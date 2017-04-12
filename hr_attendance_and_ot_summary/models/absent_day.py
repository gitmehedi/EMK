# sprite class

from openerp import models, fields

class AbsentDay(models.Model):

    _name = 'hr.attendance.absent.day'

    date = fields.Date(string='Absent Date')

    """" Relational Fields """
    att_summary_line_id = fields.Many2one("hr.attendance.summary.line", string="Weekend", required=True, ondelete='cascade')

class TempAbsentDay(object):

    def __init__(self, date=None):
        self.date = date