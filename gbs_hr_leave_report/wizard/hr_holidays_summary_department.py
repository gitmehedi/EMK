import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HRLeaveSummary(models.TransientModel):
    _name = 'hr.leave.summary.wizard'
    _description = 'HR Leaves Summary Report'

    from_date = fields.Date(string='Date From', required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    to_date = fields.Date(string='Date To', required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    operating_unit_id = fields.Many2one('operating.unit', 'Select Operating Unit', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)

    @api.multi
    def process_report(self):
        data = {}
        data['from_date'] = self.from_date
        data['to_date'] = self.to_date
        data['operating_unit_id'] = self.operating_unit_id.id

        return self.env['report'].get_action(self, 'gbs_hr_leave_report.report_emp_leave_summary', data=data)
