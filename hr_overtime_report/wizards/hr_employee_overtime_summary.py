from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AttErrorSummary(models.TransientModel):
    _name = 'hr.overtime.summary.wizard'
    _description = 'Overtime Summary Report'

    type = fields.Selection([
        ('unit_type', 'Unit Wise'),
        ('department_type', 'Department Wise'),
        ('employee_type', 'Employee Wise')
    ], string='Type', required=True)

    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', required=False,
                                        default=lambda self: self.env.user.default_operating_unit_id)

    department_id = fields.Many2one("hr.department", string="Department", required=False)

    emp_id = fields.Many2one('hr.employee', string='Employee Name', required=False)

    from_date = fields.Date('From')
    to_date = fields.Date('To')

    @api.multi
    def process_report(self):
        data = {}
        #data['type'] = self.type.id
        #data['operating_unit_id'] = self.operating_unit_id.id
        data['department_id'] = self.emp_id.department_id.id
        data['department_name'] = self.emp_id.department_id.name
        data['emp_id'] = self.emp_id.id
        data['emp_name'] = self.emp_id.name
        data['emp_desig_id'] = self.emp_id.job_id.id
        data['emp_desig_name'] = self.emp_id.job_id.name
        data['device'] = self.emp_id.device_employee_acc
        data['from_date'] = self.from_date
        data['to_date'] = self.to_date
        data['schedule'] = 'Dummy Data'
        data['actual'] = 'Dummy Data'

        return self.env['report'].get_action(self, 'hr_overtime_report.overtime_summary_report', data=data)


