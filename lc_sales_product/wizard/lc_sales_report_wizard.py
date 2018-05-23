from odoo import api, fields, models


class LcSalesReportWizard(models.TransientModel):
    _name = 'lc.sales.report.wizard'

    @api.multi
    def process_report(self):
        data = {}
        data['shipment_id'] = self.env.context.get('active_id')
        return self.env['report'].get_action(self, 'lc_sales_product.report_top_sheet', data)

