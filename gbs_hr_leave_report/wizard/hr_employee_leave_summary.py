import time
from odoo import api, fields, models, _


class HREmpLeaveSummary(models.TransientModel):
    _name = 'hr.employee.leave.summary.wizard'
    _description = 'HR Employee Leaves Summary Report'

    emp_id = fields.Many2one('hr.employee', string='Employee Name',required=True)
    from_date = fields.Date('From')
    to_date = fields.Date('To')
    department_id = fields.Many2one('hr.department', string='Department')
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)

    # @api.multi
    # def process_report(self):
    #     data = {}
    #     data['from_date'] = self.from_date
    #     data['to_date'] = self.to_date
    #     data['emp_id'] = self.emp_id.id
    #     data['emp_name'] = self.emp_id.name
    #     data['operating_unit_id'] = self.operating_unit_id.id
    #     data['operating_unit_name'] = self.operating_unit_id.name
    #
    #     if self.department_id:
    #         data['department_id'] = self.department_id.id
    #         data['department_name'] = self.department_id.name
    #     else:
    #         data['department_id'] = None
    #         data['department_name'] = None
    #
    #     return self.env['report'].get_action(self, 'gbs_hr_leave_report.report_hr_emp_leave_report', data=data)
