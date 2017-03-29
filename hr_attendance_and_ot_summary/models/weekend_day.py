from openerp import models, fields


class WeekendDay(models.Model):

    _name = 'hr.attendance.weekend.day'

    date = fields.Date(string='Weekend Date')

    """" Relational Fields """
    att_summary_line_id = fields.Many2one("hr.attendance.summary.line", string="Weekend", required=True)