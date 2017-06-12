from openerp import models, fields
from openerp import api

class DailyAttendance(models.TransientModel):
    _name = 'hr.daily.attendance'

    _description = 'Daily Attendance'

    date = fields.Date(string='Date', required=True)
    employee_id = fields.Many2one("hr.employee", string="Employee")
    department_id = fields.Many2one("hr.department", string="Department")
    report_type = fields.Selection([('department_type', 'Department wise'),
                                    ('employee_type', 'Employee wise')
                                   ], string='Report Type', required=True)
    @api.multi
    def process_report(self):
        data = {}

        data['date'] = self.date
        data['employee_id'] = self.employee_id.id

        return self.env['report'].get_action(self, 'gbs_hr_attendance_report.report_hr_daily_att', data=data)

