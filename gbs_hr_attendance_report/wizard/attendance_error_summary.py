from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError



class AttErrorSummary(models.TransientModel):
    _name = 'hr.attendance.error.summary.wizard'
    _description = 'Error Attendance Summary Report'

    type = fields.Selection([
        ('unit_type', 'Unit Wise'),
        ('department_type', 'Department Wise'),
        ('employee_type', 'Employee Wise')
    ], string='Type', required=True)

    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', required=False,
                                        default=lambda self: self.env.user.default_operating_unit_id)

    department_id = fields.Many2one("hr.department", string="Department", required=False)

    emp_id = fields.Many2one('hr.employee', string='Employee Name', required=False)

    from_date = fields.Date('From', required=True)
    to_date = fields.Date('To', required=True)

    @api.multi
    def process_report(self):
        data = {}
        data['type'] = self.type
        data['operating_unit_id'] = self.operating_unit_id.id
        data['operating_unit_name'] = self.operating_unit_id.name
        data['department_id'] = self.department_id.id
        data['department_name'] = self.department_id.name
        data['emp_id'] = self.emp_id.id
        data['emp_name'] = self.emp_id.name
        data['from_date'] = self.from_date
        data['to_date'] = self.to_date

        return self.env['report'].get_action(self, 'gbs_hr_attendance_report.report_att_error_summary', data=data)

    @api.onchange('type')
    def _onchange_type(self):
        self.operating_unit_id = None
        self.department_id = None
        self.emp_id = None

    @api.constrains('to_date','from_date')
    def _check_date(self):
        if self.to_date and self.from_date:
            if self.from_date >= self.to_date:
                raise Warning("[Error] To Date must be greater than From Date!")
