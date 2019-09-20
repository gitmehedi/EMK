from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class CreditDetailsProductWizard(models.TransientModel):
    _name = "credit.details.product.wizard"

    product_id = fields.Many2one('product.template', string='Product', domain=[('sale_ok', '=', 1), ('active', '=', 1)])
    # date_from = fields.Date("Date From", required=True)
    # date_to = fields.Date("Date To", required=True)

    # @api.constrains('date_from', 'date_to')
    # def _check_date_validation(self):
    #     if self.date_from > self.date_to:
    #         raise ValidationError(_("From date must be less then To date."))
    #     elif (datetime.strptime(self.date_to, '%Y-%m-%d') - datetime.strptime(self.date_from, '%Y-%m-%d')).days > 365:
    #         raise ValidationError(_("Maximum date range is one year."))

    @api.multi
    def process_print(self):
        data = dict()
        data['product_id'] = self.product_id.id
        data['product_name'] = self.product_id.name
        # data['date_from'] = self.date_from
        # data['date_to'] = self.date_to

        return self.env['report'].get_action(self, 'samuda_sales_report.report_credit_details_product', data=data)
