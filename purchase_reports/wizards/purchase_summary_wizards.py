from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
import datetime

class PurchaseSummaryWizard(models.TransientModel):
    _name = "purchase.summary.wizard"


    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit')
    # dept_location_id = fields.Many2one('stock.location', string='Department',
    #                                    domain=[('usage', '=', 'departmental')])
    date_from = fields.Date("Date From", required=True)
    date_to = fields.Date("Date To", required=True)

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        date_from= datetime.datetime.strptime(self.date_from, "%Y-%m-%d")
        date_to= datetime.datetime.strptime(self.date_to, "%Y-%m-%d")

        difference = relativedelta(date_from, date_to)
        month = abs(difference.months)
        if month > 5:
            raise Warning("Date from and Date to don't select more then 4 month")

    @api.multi
    def process_print(self):
        data = {}
        data['report_type'] = self.env.context.get('type')
        data['operating_unit_id'] = self.operating_unit_id.name
        data['date_from'] = self.date_from
        data['date_to'] = self.date_to

        return self.env['report'].get_action(self, 'purchase_reports.purchase_summary_template', data=data)
