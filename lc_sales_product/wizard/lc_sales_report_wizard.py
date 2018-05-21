from odoo import api, fields, models


class LcSalesReportWizard(models.TransientModel):
    _name = 'lc.sales.report.wizard'

    @api.multi
    def process_report(self):
        data = {}

        return self.env['report'].get_action(self, 'gbs_hr_leave_report.hr_emp_leave_report', data=data)

