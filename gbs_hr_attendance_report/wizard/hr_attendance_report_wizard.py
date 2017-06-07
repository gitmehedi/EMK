from openerp import models, fields, api

class HrBankSelectionWizard(models.TransientModel):
    _name = 'hr.attendance.report.wizard'

    check_in_out = fields.Selection([
        ('check_in', 'Check In'),
        ('check_out', 'Check Out'),
        ], string = 'Check Type', required=True, default="check_in")

    type = fields.Selection([
        ('department_type', 'Department wise'),
        ('employee_type', 'Employee wise')
    ], string='Type', required=True)

    department_id = fields.Many2one("hr.department", string="Department", required=False)
    employee_id = fields.Many2one("hr.employee", string="Employee")
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')

    @api.multi
    def process_report(self):

        data = {}

        data['check_in_out'] = self.check_in_out
        data['type'] = self.type
        data['department_id'] = self.department_id.id
        data['employee_id'] = self.employee_id.id
        data['from_date'] = self.from_date
        data['to_date'] = self.to_date

        return self.env['report'].get_action(self, 'gbs_hr_attendance_report.report_individual_payslip', data=data)

