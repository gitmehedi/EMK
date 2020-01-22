from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class HRLeaveSummary(models.TransientModel):
    _name = 'hr.leave.summary.wizard'
    _description = 'HR Leaves Summary Report'

    year_id = fields.Many2one('date.range', string='Leave Year',required=True,
                              domain="[('type_id.holiday_year', '=', True)]")
    #new_fields
    from_date = fields.Date('From')
    to_date = fields.Date('To')
    #new_fieds
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
        data['from_date'] = self.from_date
        data['to_date'] = self.to_date

        if self.department_id:
            data['department_id'] = self.department_id.id
            data['department_name'] = self.department_id.name
        else:
            data['department_id'] = None
            data['department_name'] = None

        return self.env['report'].get_action(self, 'gbs_hr_leave_report.report_emp_leave_summary', data=data)

    @api.constrains('to_date', 'from_date')
    def _check_date(self):
        if self.to_date and self.from_date:
            if self.from_date >= self.to_date:
                raise Warning("[Error] To Date must be greater than From Date!")
        return True

    @api.constrains('to_date', 'from_date', 'year_id')
    def _check_year(self):
        if self.to_date and self.from_date:
            if self.from_date >= self.year_id.date_start and self.to_date <= self.year_id.date_end:
                pass
            else:
                raise ValidationError(_('Leave duration starting date and ending date should be same year!!'))
