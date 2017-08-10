from odoo import api, fields, models,tools
from datetime import date


class HrAttendanceUtilities(models.Model):
    _name = "hr.attendance.utilities"
    _auto = False




    @api.multi
    def _get_shifting(self):
        return 'OK'