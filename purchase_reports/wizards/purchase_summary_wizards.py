from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
import datetime

class PurchaseSummaryWizard(models.TransientModel):
    _name = "purchase.summary.wizard"


    operating_unit_ids = fields.Many2many('operating.unit',string='Operating Unit')
    # indent_ids = fields.Many2many('operating.unit','pur_ou_rel','pur_id','ou_id',string='Operating Unit')

    pur_month_ids = fields.Many2many('date.range', string="Month",required = True,
                                    domain="[('type_id.purchase_month', '=', True)]")

    # @api.constrains('date_from', 'date_to')
    # def _check_date(self):
    #     date_from= datetime.datetime.strptime(self.date_from, "%Y-%m-%d")
    #     date_to= datetime.datetime.strptime(self.date_to, "%Y-%m-%d")
    #
    #     difference = relativedelta(date_from, date_to)
    #     month = abs(difference.months)
    #     if month > 5:
    #         raise Warning("Date from and Date to don't select more then 4 month")

    @api.multi
    def process_print(self):
        data = {}
        months = []
        operating_unit = []
        data['report_type'] = self.env.context.get('type')
        for ou in self.operating_unit_ids:
            operating_unit.append(ou.id)
        data['operating_unit_id']=operating_unit
        for month in self.pur_month_ids:
            months.append(month.id)
        data['pur_month'] = months

        return self.env['report'].get_action(self, 'purchase_reports.purchase_summary_template', data=data)
