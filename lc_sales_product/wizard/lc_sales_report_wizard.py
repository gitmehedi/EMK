from odoo import api, fields, models


class LcSalesReportWizard(models.TransientModel):
    _name = 'lc.sales.report.wizard'

    @api.multi
    def process_report(self):
        data = {}

        return self.env['report'].get_action(self, 'lc_sales_product.report_top_sheet', data=data)

