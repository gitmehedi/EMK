from odoo import api, fields, models
import datetime


class GenerateMonthlyDeliveryReport(models.Model):
    _name = 'monthly.delivery.report.wizard'

    report_to = fields.Datetime(string="Report To", required=True,)
    report_from = fields.Datetime(string="Report From", required=True, )
    product_id = fields.Many2one('product.product', string='Product',required=True,)

    @api.multi
    def process_monthly_delivery_report(self):
        return self.env['report'].get_action(self, 'delivery_qty_reports.report_monthly_delivery_products',
                                           data={'product_id': self.product_id.id,'report_to': self.report_to,'report_from': self.report_from})
