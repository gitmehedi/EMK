from odoo import fields, models, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

class ExpReference(models.TransientModel):
    _name = 'exp.reference.report'

    date_from = fields.Date(string='From', required=True)
    date_to = fields.Date(string='To', required=True)
    type = fields.Selection([('local', 'Local'), ('foreign', 'Foreign')], required=True)
    is_readonly_type = fields.Boolean('Is Readonly Type?', default=False)

    @api.multi
    def report_print(self):
        self.ensure_one()
        ReportUtility = self.env['report.utility']
        date_to = datetime.strptime(ReportUtility.get_date_from_string(self.date_to), '%d-%m-%Y')
        date_from = datetime.strptime(ReportUtility.get_date_from_string(self.date_from), '%d-%m-%Y')
        diff_days = date_to - date_from
        if diff_days.days > 365:
            raise UserError('You can\'t generate report greater than 12 months')

        return self.env['report'].get_action(self, 'lc_sales_local_report.exp_reference_report')