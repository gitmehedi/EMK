from odoo import models, fields, api

class ProvidentFundWizard(models.TransientModel):
    _name = "provident.fund.wizard"

    employee_id = fields.Many2one('hr.employee', string="Employee Name", required=True)

    @api.multi
    def process_print(self):
        ReportUtility = self.env['report.utility']
        data = {}
        data['employee_id'] = self.employee_id.name
        data['emp_id'] = self.employee_id.id
        data['department_id'] = self.employee_id.department_id.name
        data['job_id'] = self.employee_id.job_id.name
        # data['initial_employment_date'] = self.employee_id.initial_employment_date
        data['initial_employment_date'] = ReportUtility.get_date_from_string(self.employee_id.initial_employment_date)

        data['device_employee_acc'] = self.employee_id.device_employee_acc
        data['total_pf'] = self.employee_id.total_pf

        return self.env['report'].get_action(self, 'gbs_hr_payroll.report_individual_provident_fund', data=data)
