from odoo import models, fields, api

class PayslipReportWizard(models.TransientModel):
    _name = "payslip.report.wizard"

    @api.multi
    def process_cash_salary_print(self):
        data = {}
        data['active_id'] = self.env.context.get('active_id')
        data['report_type'] = 'cash'
        return self.env['report'].get_action(self, 'gbs_hr_payroll.report_individual_payslip', data)

    @api.multi
    def process_payslip_summary_print(self):
        data = {}
        data['active_id'] = self.env.context.get('active_id')
        data['report_type'] = 'all'
        return self.env['report'].get_action(self, 'gbs_hr_payroll.report_individual_payslip', data)

    @api.multi
    def process_pf_report(self):
        data = {}
        data['active_id'] = self.env.context.get('active_id')
        return self.env['report'].get_action(self,'gbs_hr_payroll.report_provident_fund_unit_wise',data)

    @api.multi
    def process_loan_deduction_print(self):
        data = {}
        data['active_id'] = self.env.context.get('active_id')
        return self.env['report'].get_action(self,'gbs_hr_payroll.report_monthly_loan_deduction',data)

    @api.multi
    def process_top_sheet_print(self):
        data = {}
        data['active_id'] = self.env.context.get('active_id')
        return self.env['report'].get_action(self,'gbs_hr_payroll_top_sheet.report_top_sheet',data)

    @api.multi
    def process_cost_center_wise_top_sheet(self):
        data = {}
        data['active_id'] = self.env.context.get('active_id')
        # return self.env['report'].get_action(self, 'gbs_hr_payroll_top_sheet.report_top_sheet', data)
        active_id = self.env.context.get('active_id')
        return {
            'name': 'Cost Center Wise Top Sheet',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cost.center.top.sheet.wizard',
            'context': {'active_id': active_id},
            'target': 'new',
        }
