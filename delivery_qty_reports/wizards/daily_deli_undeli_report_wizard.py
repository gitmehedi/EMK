from odoo import api, fields, models
import datetime


class DailyDeliveryUnDeliveryReport(models.TransientModel):
    _name = 'daily.delivery.undelivery.report.wizard'

    report_of_day = fields.Date(string="Report of day", required=True, )
    product_id = fields.Many2one('product.product', string='Product', domain="([('sale_ok','=','True')])",
                                 required=False, )


    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit',
                                        required='True', default=lambda self: self.env.user.default_operating_unit_id)


    @api.multi
    def process_delivery_report(self):
        data = {
            'report_of_day': self.report_of_day,
            'operating_unit_id': self.operating_unit_id.id,
            'operating_unit_name': self.operating_unit_id.name
        }

        return self.env['report'].get_action(self, 'delivery_qty_reports.report_daily_deli_undeli', data=data)
