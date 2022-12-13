from odoo import fields, models, api
from datetime import datetime, timedelta

class ExpReference(models.TransientModel):
    _name = 'exp.reference.report'

    date_from = fields.Date(string='From', default=fields.Datetime.now, required=True)
    date_to = fields.Date(string='To', default=fields.Datetime.now, required=True)
    type = fields.Selection([('all', 'All'), ('local', 'Local'), ('foreign', 'Foreign')], default='all', required=True)


    @api.multi
    def report_print(self):
        self.ensure_one()
        ReportUtility = self.env['report.utility']
        date_to = datetime.strptime(ReportUtility.get_date_from_string(self.date_to), '%d-%m-%Y')
        date_from = datetime.strptime(ReportUtility.get_date_from_string(self.date_from), '%d-%m-%Y')
        diff_days = date_to - date_from
        if diff_days.days > 180:
            raise UserError('You can\'t generate report greater than 6 months')

        return self.env['report'].get_action(self, 'lc_sales_local_report.exp_reference_report')