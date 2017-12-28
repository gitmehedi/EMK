import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HRLeaveSummary(models.TransientModel):
    _name = 'hr.leave.summary.wizard'
    _description = 'HR Leaves Summary Report'

    year_id = fields.Many2one('hr.leave.fiscal.year', string='Leave Year',required=True)
    department_id = fields.Many2one('hr.department', string='Department')
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)

    @api.multi
    def process_report(self):
        data = {}
        data['department_id'] = self.department_id.id
        data['department_name'] = self.department_id.name
        data['year_id'] = self.year_id.id
        data['year_name'] = self.year_id.name
        data['operating_unit_id'] = self.operating_unit_id.id

        if self.operating_unit_id.name == 'All':
            data['operating_unit_name'] = False
        else:
            data['operating_unit_name'] = self.operating_unit_id.name

        return self.env['report'].get_action(self, 'gbs_hr_leave_report.report_emp_leave_summary', data=data)
