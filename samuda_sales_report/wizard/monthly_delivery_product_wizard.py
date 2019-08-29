from odoo import models, fields, api, _
from datetime import datetime
import calendar


class MonthlyDeliveryProductWizard(models.TransientModel):
    _name = "monthly.delivery.product.wizard"

    type = fields.Selection([
        ('local', 'Local'),
        ('foreign', 'Foreign')
    ], string='Type', default='local')

    product_id = fields.Many2one('product.template', string='Product', domain=[('sale_ok', '=', 1), ('active', '=', 1)],
                                 required=True)
    month = fields.Selection([(m, calendar.month_name[m]) for m in range(1, 13)], 'Month', required=True)
    year = fields.Selection([(int(num), int(num)) for num in reversed(range(2018, datetime.now().year + 1))],
                            'Year', required=True)

    @api.multi
    def process_print(self):
        data = dict()
        data['type'] = self.type
        data['product_id'] = self.product_id.id
        data['product_name'] = self.product_id.name
        data['month'] = self.month
        data['month_name'] = calendar.month_name[self.month]
        data['month_days'] = calendar.monthrange(self.year, self.month)[1]
        data['year'] = self.year

        return self.env['report'].get_action(self, 'samuda_sales_report.report_monthly_delivery_product', data=data)
