from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class CustomerSalesSectorWizard(models.TransientModel):
    _name = "customer.sales.sector.wizard"

    sector_id = fields.Many2one('res.partner.category', string='Sector')
    date_from = fields.Date("Date From", required=True)
    date_to = fields.Date("Date To", required=True)

    @api.constrains('date_from', 'date_to')
    def _check_date_validation(self):
        if self.date_from > self.date_to:
            raise ValidationError(_("From date must be less then To date."))
        elif (datetime.strptime(self.date_to, '%Y-%m-%d') - datetime.strptime(self.date_from, '%Y-%m-%d')).days > 365:
            raise ValidationError(_("Maximum date range is one year."))

    @api.multi
    def process_print(self):
        data = dict()
        data['sector_id'] = self.sector_id.id
        data['sector_name'] = self.sector_id.name
        data['date_from'] = self.date_from
        data['date_to'] = self.date_to

        return self.env['report'].get_action(self, 'samuda_sales_report.report_customer_sales_sector', data=data)
