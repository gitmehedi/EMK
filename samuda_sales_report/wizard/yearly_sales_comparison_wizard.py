from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class YearlySalesComparisonWizard(models.TransientModel):
    _name = "yearly.sales.comparison.wizard"

    year_first = fields.Selection([(str(num), str(num)) for num in reversed(range(2018, datetime.now().year + 1))],
                                  'First Year', required=True)
    year_last = fields.Selection([(str(num), str(num)) for num in reversed(range(2018, datetime.now().year + 1))],
                                 'Last Year', required=True)

    @api.constrains('year_first', 'year_last')
    def _check_date_validation(self):
        if self.year_first == self.year_last:
            raise ValidationError(_("Year must be different."))

    @api.multi
    def process_print(self):
        data = dict()
        data['year_first'] = self.year_first
        data['year_last'] = self.year_last

        return self.env['report'].get_action(self, 'samuda_sales_report.report_yearly_sales_comparison', data=data)
