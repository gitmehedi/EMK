from odoo import models, fields, api

class ProvidentFundWizard(models.TransientModel):
    _name = "provident.fund.wizard"

    def _current_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    employee_id = fields.Many2one('hr.employee', string="Employee Name", required=True, default=_current_employee)
    compute_field = fields.Boolean(string="check field", compute='get_user')

    @api.depends('employee_id')
    def get_user(self):
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if not res_user.has_group('hr.group_hr_user') or not res_user.has_group('hr.group_hr_manager'):
            self.compute_field = True
        else:
            self.compute_field = False

    @api.multi
    def process_print(self):
        data = {}
        data['employee_id'] = self.employee_id.name
        data['emp_id'] = self.employee_id.id
        data['department_id'] = self.employee_id.department_id.name
        data['job_id'] = self.employee_id.job_id.name
        data['initial_employment_date'] = self.employee_id.initial_employment_date
        data['device_employee_acc'] = self.employee_id.device_employee_acc
        data['total_pf'] = self.employee_id.total_pf

        return self.env['report'].get_action(self, 'gbs_hr_payroll.report_individual_provident_fund', data=data)
