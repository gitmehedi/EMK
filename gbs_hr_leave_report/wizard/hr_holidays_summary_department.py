from odoo import api, fields, models, _

class HRLeaveSummary(models.TransientModel):
    _name = 'hr.leave.summary.wizard'
    _description = 'HR Leaves Summary Report'

    year_id = fields.Many2one('date.range', string='Leave Year',required=True,
                              domain="[('type_id.holiday_year', '=', True)]")
    department_id = fields.Many2one('hr.department', string='Department')
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)

    @api.multi
    def process_report(self):
        data = {}
        data['year_id'] = self.year_id.id
        data['year_name'] = self.year_id.name
        data['operating_unit_id'] = self.operating_unit_id.id
        data['operating_unit_name'] = self.operating_unit_id.name

        if self.department_id:
            data['department_id'] = self.department_id.id
            data['department_name'] = self.department_id.name
        else:
            data['department_id'] = None
            data['department_name'] = None

        return self.env['report'].get_action(self, 'gbs_hr_leave_report.report_emp_leave_summary', data=data)
