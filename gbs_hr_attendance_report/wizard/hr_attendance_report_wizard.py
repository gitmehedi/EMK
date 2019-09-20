from openerp import models, fields, api

class HrAttendanceReportWizard(models.TransientModel):
    _name = 'hr.attendance.report.wizard'

    check_in_out = fields.Selection([
        ('check_in', 'Check In'),
        ('check_out', 'Check Out'),
        ], string = 'Check Type', default="check_in", required=True)

    type = fields.Selection([
        ('op_type', 'Operating Unit wise'),
        ('department_type', 'Department wise'),
        ('employee_type', 'Employee wise')
    ], string='Type', required=True)

    operating_unit_id = fields.Many2one('operating.unit', 'Select Operating Unit', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)
    department_id = fields.Many2one("hr.department", string="Department")
    employee_id = fields.Many2one("hr.employee", string="Employee")
    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)

    @api.multi
    def process_report(self):

        data = {}
        data['check_in_out'] = self.check_in_out
        data['type'] = self.type
        data['operating_unit_id'] = self.operating_unit_id.id
        data['department_id'] = self.department_id.id
        data['employee_id'] = self.employee_id.id
        data['from_date'] = self.from_date
        data['to_date'] = self.to_date

        return self.env['report'].get_action(self, 'gbs_hr_attendance_report.report_attendance_doc', data=data)
