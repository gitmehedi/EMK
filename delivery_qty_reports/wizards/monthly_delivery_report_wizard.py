from odoo import api, fields, models
import datetime


class GenerateMonthlyDeliveryReport(models.Model):
    _name = 'monthly.delivery.report.wizard'

    report_of_month = fields.Datetime(string="Report of Month", required=True, )
    product_id = fields.Many2one('product.product', string='Product')

    @api.multi
    def process_monthly_delivery_report(self):
        return self.env['report'].get_action(self, 'delivery_qty_reports.report_monthly_delivery_products',
                                           data={'product_id':self.product_id.id,'report_of_month': self.report_of_month})
