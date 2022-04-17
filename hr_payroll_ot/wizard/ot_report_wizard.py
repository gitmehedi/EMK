from odoo import fields, models, api

class OtReportWizard(models.TransientModel):
    _name = 'ot.report.wizard'
    hr_payslip_run_id = fields.Many2one('hr.payslip.run', string='Payslip Run')

    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        return self.env['report'].get_action(self, report_name='hr_payroll_ot.monthly_ot_sheet_xlsx')
