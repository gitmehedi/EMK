from odoo import models, fields, api, _


class DailyDeliveryStatementWizard(models.TransientModel):
    _name = "daily.delivery.statement.wizard"

    executive_id = fields.Many2one('res.users', string='Executive', required=True)
    date_delivery = fields.Date("Date", required=True)

    @api.multi
    def process_print(self):
        data = dict()
        data['executive_id'] = self.executive_id.id
        data['executive_name'] = self.executive_id.name
        data['date_delivery'] = self.date_delivery

        return self.env['report'].get_action(self, 'samuda_sales_report.report_daily_delivery_statement', data=data)
