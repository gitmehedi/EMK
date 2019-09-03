from odoo import models, fields, api, _
from datetime import datetime
import calendar


class MonthlyDeliveryExecutiveWizard(models.TransientModel):
    _name = "monthly.delivery.executive.wizard"

    # here executive_id is user_id
    executive_id = fields.Many2one('res.users', string='Executive', required=True)
    month = fields.Selection([(m, calendar.month_name[m]) for m in range(1, 13)], 'Month', required=True)
    year = fields.Selection([(int(num), int(num)) for num in reversed(range(2018, datetime.now().year + 1))],
                            'Year', required=True)

    @api.onchange('executive_id')
    def _onchange_executive_id(self):
        user_ids = self.env['res.groups'].search([('name', '=', 'User: All Documents')]).users.ids

        return {'domain': {'executive_id': [('id', 'in', user_ids)]}}

    @api.multi
    def process_print(self):
        data = dict()
        data['executive_id'] = self.executive_id.id
        data['executive_name'] = self.executive_id.name
        data['month'] = self.month
        data['month_name'] = calendar.month_name[self.month]
        data['month_days'] = calendar.monthrange(self.year, self.month)[1]
        data['year'] = self.year

        return self.env['report'].get_action(self, 'samuda_sales_report.report_monthly_delivery_executive', data=data)
