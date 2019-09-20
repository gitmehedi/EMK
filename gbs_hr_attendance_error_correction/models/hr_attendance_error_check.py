from openerp import models, fields
from openerp import api

class AttendanceCheckError(models.Model):
    _inherit = 'hr.attendance'

    _order = "id"

    has_error = fields.Boolean(default=False, string='has_error', compute='onchange_attendance_data', store=True)
    check_in = fields.Datetime(string="Check In", required=False)
    duty_date = fields.Date(string='Duty Date', required=False)

    @api.depends('check_in', 'check_out')
    def onchange_attendance_data(self):
        for att in self:
            if (att.check_in is None) or (att.check_out is None):
                att.has_error = True

            elif att.check_out < att.check_in:
                att.has_error = True

            else:
                att.has_error = False