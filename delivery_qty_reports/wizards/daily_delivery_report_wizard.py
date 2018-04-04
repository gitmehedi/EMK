from odoo import api, fields, models
import datetime


class GenerateDailyDeliveryReport(models.Model):
    _name = 'daily.delivery.report.wizard'

    report_of_day = fields.Datetime(string="Report of day", required=True, )

    @api.multi
    def process_delivery_report(self):
        return self.env['report'].get_action(self, 'delivery_qty_reports.report_daily_delivery_products',
                                           data={'report_of_day': self.report_of_day})
