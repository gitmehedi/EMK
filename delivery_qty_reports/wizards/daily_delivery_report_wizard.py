from odoo import api, fields, models
import datetime

class GenerateDailyDeliveryReport(models.Model):
    _name = 'daily.delivery.report.wizard'

    report_of_day = fields.Date(string="Report of day", required=True,)

    @api.multi
    def process_delivery_report(self):
        print 'Button clicked!!'
