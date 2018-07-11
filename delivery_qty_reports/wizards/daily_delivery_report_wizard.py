from odoo import api, fields, models
import datetime


class GenerateDailyDeliveryReport(models.Model):
    _name = 'daily.delivery.report.wizard'

    report_of_day = fields.Datetime(string="Report of day", required=True, )
    product_id = fields.Many2one('product.product', string='Product', domain="([('sale_ok','=','True')])",
                                 required=True, )
    operating_unit_id = fields.Many2one('operating.unit', string='OP Unit', required=True)

    @api.multi
    def process_delivery_report(self):
        data = {
            'report_of_day': self.report_of_day,
            'product_id': self.product_id.id,
            'operating_unit_id': self.operating_unit_id.id
        }

        return self.env['report'].get_action(self, 'delivery_qty_reports.report_daily_delivery_products', data=data)
