from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AttendanceSummaryReportWizard(models.TransientModel):
    _name = 'attendance.summary.report.wizard'

    department_id = fields.Many2many('hr.department', string='Department')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id.id)
    operating_unit_id = fields.Many2many('operating.unit', string='Operating Unit', domain="[('company_id', '=', company_id)]")
    date_from = fields.Date('From', required=True)
    date_to = fields.Date('To', required=True)
    employee_tag_ids = fields.Many2many('hr.employee.category', string='Employee Tag')

    multi_company = fields.Boolean(string="check field", compute='get_multi_company_user')

    @api.depends('company_id')
    def get_multi_company_user(self):
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if not res_user.has_group('base.group_multi_company'):
            self.multi_company = True
        else:
            self.multi_company = False

    @api.multi
    def process_report(self):
        data = {}
        ou_name = ''
        data['company_id'] = self.company_id.id
        if not self.department_id:
            dept_env = self.env['hr.department'].search([('company_id', '=', self.company_id.id)])
            data['department_id'] = dept_env.ids
        else:
            data['department_id'] = self.department_id.ids
        if not self.operating_unit_id:
            ou_env = self.env['operating.unit'].search([('company_id', '=', self.company_id.id)])
            data['operating_unit_id'] = ou_env.ids
            ou_name = 'All'
        else:
            data['operating_unit_id'] = self.operating_unit_id.ids
            for record in self.operating_unit_id:
                ou_name += str(record.name) + '  '
        data['emp_tag_ids'] = self.employee_tag_ids.ids
        data['date_from'] = self.date_from
        data['date_to'] = self.date_to
        data['company_name'] = self.company_id.name
        data['ou_name'] = ou_name

        return self.env['report'].get_action(self, 'gbs_hr_attendance_report.report_att_summ_temp', data=data)

    @api.constrains('date_to', 'date_from')
    def _check_date(self):
        if self.date_to and self.date_from:
            if self.date_from > self.date_to:
                raise ValidationError("[Error] To Date must be greater than or equal to From Date!")
        return True