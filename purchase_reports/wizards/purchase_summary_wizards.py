from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
import datetime

class PurchaseSummaryWizard(models.TransientModel):
    _name = "purchase.summary.wizard"


    operating_unit_ids = fields.Many2many('operating.unit',string='Operating Unit')

    pur_month = fields.Selection([
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August')
    ], string='Month', required=True)

    pur_year = fields.Selection([
        ('1','2018'),
        ('2','2019'),
        ('3','2020'),
        ('4','2021'),
        ('5','2022'),
        ('6','2023'),
        ('7','2024'),
        ('8','2025')],string="Year",required=True)


    @api.multi
    def process_print(self):
        data = {}
        months = []
        operating_unit = []
        data['report_type'] = self.env.context.get('type')
        for ou in self.operating_unit_ids:
            operating_unit.append(ou.name)
        data['operating_unit_name']=operating_unit

        for month in range(int(self.pur_month), int(self.pur_month) + 4):
            str_month = str(month)
            string_velue = dict(self._fields['pur_month'].selection).get(str_month)
            months.append(string_velue)
        data['purchase_month'] = months
        data['pur_year'] = dict(self._fields['pur_year'].selection).get(self.pur_year)

        return self.env['report'].get_action(self, 'purchase_reports.purchase_summary_template', data=data)
