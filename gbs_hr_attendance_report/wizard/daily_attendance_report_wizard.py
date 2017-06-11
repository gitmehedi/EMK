from openerp import models, fields
from openerp import api

class DailyAttendance(models.TransientModel):
    _name = 'hr.daily.attendance'

    _description = 'Daily Attendance'

    date = fields.Date(string='Date', required=True)
    department_id = fields.Many2one("hr.department", string="Department")
    employee_id = fields.Many2one("hr.employee", string="Employee")

    report_type = fields.Selection([
        ('department_type', 'Department wise'),
        ('employee_type', 'Employee wise')
    ], string='Report Type', required=True)

    @api.multi
    def check_report(self):
        data = {}
        data['form'] = self.read(['department_id', 'employee_id', 'date'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['department_id', 'employee_id', 'date'])[0])
        return self.env['report'].get_action(self, 'gbs_hr_attendance_report.report_daily_attendance', data=data)

    # @api.multi
    # def check_report(self):
    #     data = {}
    #
    #     data['report_type'] = self.report_type
    #     data['department_id'] = self.department_id.id
    #     data['employee_id'] = self.employee_id.id
    #     data['date'] = self.date
    #
    #
    #     return self.env['report'].get_action(self, 'gbs_hr_attendance_report.report_daily_attendance', data=data)

