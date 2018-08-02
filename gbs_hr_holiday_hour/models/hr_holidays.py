from datetime import datetime
import math
from odoo import api, fields, models
from datetime import timedelta


class HrEmployee(models.Model):

    _inherit = "hr.short.leave"

    holiday_status_id = fields.Many2one("hr.holidays.status", string="Leave Type", required=True, readonly=True,
                                        domain="[('short_leave_flag','=',True)]",
                                        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})

    @api.multi
    def action_validate(self):
        res = super(HrEmployee, self).action_validate()
        from_dt = fields.Datetime.from_string(self.date_from)
        to_dt = fields.Datetime.from_string(self.date_to)
        time_delta = to_dt - from_dt

        self.env['hr.holidays'].create(
            {'short_leave_ids': self.id,
             'type': 'remove',
             'holiday_status_id': self.holiday_status_id.id,
             'date_from': self.date_from,
             'date_to': self.date_to,
             'number_of_days_temp': (time_delta.seconds/3600)/8.0,
             'employee_id': self.employee_id.id,
             })

        return res



class HrShortLeave(models.Model):
    _inherit = 'hr.holidays.status'

    short_leave_flag = fields.Boolean(string='Allow Short Leave', default=False)
