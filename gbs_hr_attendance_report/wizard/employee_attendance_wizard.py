from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class GbsEmployeeAttendanceWizard(models.TransientModel):
    _name = 'gbs.employee.attendance.wizard'
    _description = 'Employee Attendance Report'

    def _current_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    employee_id = fields.Many2one('hr.employee', string="Employee Name", default=_current_employee, required=True)
    date_from = fields.Date('From', required=True)
    date_to = fields.Date('To')
    compute_field = fields.Boolean(string="check field", compute='get_user')

    @api.depends('employee_id')
    def get_user(self):
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if not res_user.has_group('hr_attendance.group_hr_attendance_manager'):
            self.compute_field = True
        else:
            self.compute_field = False

    @api.multi
    def process_report(self):

        data = {}
        data['employee_id'] = self.employee_id.id
        data['name'] = self.employee_id.name_related
        data['dept'] = self.employee_id.department_id.name
        data['designation'] = self.employee_id.job_id.name
        data['date_from'] = self.date_from
        data['date_to'] = self.date_to if self.date_to else datetime.now().strftime('%Y-%m-%d')

        return self.env['report'].get_action(self, 'gbs_hr_attendance_report.gbs_employee_attendance_doc', data=data)

    @api.constrains('date_to', 'date_from')
    def _check_date(self):
        if self.date_to and self.date_from:
            if self.date_from > self.date_to:
                raise Warning("[Error] To Date must be greater than or equal to From Date!")
        return True