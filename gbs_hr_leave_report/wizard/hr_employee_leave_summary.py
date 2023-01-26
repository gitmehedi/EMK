from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError



class HREmpLeaveSummary(models.TransientModel):
    _name = 'hr.employee.leave.summary.wizard'
    _description = 'HR Employee Leaves Summary Report'

    emp_id = fields.Many2one('hr.employee', string='Employee Name', required=True,
                             domain=[('operating_unit_id', '=', 'self.operating_unit_id')])
    from_date = fields.Date('From')
    to_date = fields.Date('To')
    year_id = fields.Many2one('date.range', string='Leave Year', required=True,
                              domain="[('type_id.holiday_year', '=', True)]")
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)

    @api.multi
    def process_report(self):
        data = {}
        data['emp_id'] = self.emp_id.id
        data['emp_name'] = self.emp_id.name
        data['emp_acc'] = self.emp_id.device_employee_acc
        data['designation'] = self.emp_id.job_id.name
        data['department'] = self.emp_id.department_id.name
        data['operating_unit_id'] = self.operating_unit_id.id
        data['operating_unit_name'] = self.operating_unit_id.name
        data['department_id'] = self.emp_id.department_id.id
        data['year_id'] = self.year_id.id
        data['year_name'] = self.year_id.name
        data['from_date'] = self.from_date
        data['to_date'] = self.to_date

        return self.env['report'].get_action(self, 'gbs_hr_leave_report.hr_emp_leave_report', data=data)

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):
        if self.operating_unit_id:
            unit_obj = self.env['hr.employee'].search([('operating_unit_id', '=', self.operating_unit_id.id)])
            return {'domain': {
                'emp_id': [('id', 'in', unit_obj.ids)]
            }
            }

    @api.constrains('to_date','from_date')
    def _check_date(self):
        if self.to_date and self.from_date:
            if self.from_date > self.to_date:
                raise Warning("[Error] To Date must be greater than or equal to From Date!")

    @api.constrains('to_date','from_date','year_id')
    def _check_year(self):
        if self.to_date and self.from_date:
            if self.from_date >= self.year_id.date_start and self.to_date <= self.year_id.date_end:
                pass
            else:
                raise ValidationError(_('Leave duration starting date and ending date should be same year!!'))