from odoo import api, fields, models
import datetime


class GenerateMonthlyDeliveryReport(models.TransientModel):
    _name = 'monthly.delivery.report.wizard'

    report_to = fields.Date(string="Report To", required=True,)
    report_from = fields.Date(string="Report From", required=True, )
    product_id = fields.Many2one('product.product', string='Product',required=True,domain="([('sale_ok','=','True')])",)
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit',
                                        required='True', default=lambda self: self.env.user.default_operating_unit_id)

    @api.multi
    def process_monthly_delivery_report(self):
        return self.env['report'].get_action(self, 'delivery_qty_reports.report_monthly_delivery_products',
                                           data={'operating_unit_id':self.operating_unit_id.id, 'product_id': self.product_id.id,'report_to': self.report_to,'report_from': self.report_from})
