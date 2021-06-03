# imports of python library
import datetime

# imports of odoo
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class AnalyticAccountWizard(models.TransientModel):
    _name = 'analytic.account.wizard'

    date_from = fields.Date("Date From", required=True)
    date_to = fields.Date("Date To", required=True)
    all_entries = fields.Boolean(string='Include Unposted Entries', default=False)
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit')
    cost_center_id = fields.Many2one('account.cost.center', string='Cost Center')

    @api.constrains('date_from', 'date_to')
    def _check_date_range(self):
        dt_range = self.env['date.range'].search(
            [('type_id.fiscal_year', '=', True), ('date_start', '<=', self.date_from),
             ('date_end', '>=', self.date_from)])
        dt_from = datetime.datetime.strptime(self.date_from, '%Y-%m-%d')
        dt_to = datetime.datetime.strptime(self.date_to, '%Y-%m-%d')

        if dt_from.year != dt_to.year:
            raise ValidationError(_("Date From and Date To must be the same financial year."))
        if self.date_from > self.date_to:
            raise ValidationError(_("From date must be less then To date."))
        if not dt_range.date_start and not dt_range.date_end:
            raise ValidationError(_("Date range of fiscal year does not exist."))

    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        return self.env['report'].get_action(self, report_name='samuda_account_reports.analytic_account_xlsx')
