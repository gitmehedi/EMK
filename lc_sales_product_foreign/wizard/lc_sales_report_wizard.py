from odoo import api, fields, models


class LcSalesReportWizard(models.TransientModel):
    _name = 'lc.sales.report.foreign.wizard'

    @api.multi
    def process_packing_list(self):
        data = {}
        data['shipment_id'] = self.env.context.get('active_id')
        return self.env['report'].get_action(self, 'lc_sales_product_foreign.report_packing_list', data)

    @api.multi
    def process_commercial_invoice(self):
        return self.env['report'].get_action(self, 'lc_sales_product_foreign.report_commercial_invoice',
                                             {'lc_id': self.env.context.get('active_id')})
