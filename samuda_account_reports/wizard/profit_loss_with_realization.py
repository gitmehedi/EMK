import calendar
from odoo import api, fields, models , _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta, datetime


class ProfitLossRealizationWizard(models.TransientModel):
    _name = 'profit.loss.realization.wizard'

    date_from = fields.Date("Start date")
    date_to = fields.Date("End date")
    date_filter = fields.Selection([('this_month', 'This Month'), ('this_quarter', 'This Quarter'),
                                    ('this_year', 'This Financial Year'), ('last_month', 'Last Month'),
                                    ('last_quarter', 'Last Quarter'), ('last_year', 'Last Financial Year'),
                                    ('custom', 'Custom')], default='this_month', required=True)

    comparison = fields.Boolean(compute='_get_comparison', string='Enable comparison', default=False)
    date_from_cmp = fields.Date("Start date for comp.",
                                default=lambda s: datetime.today() + timedelta(days=-395))
    date_to_cmp = fields.Date("End date for comp.",
                              default=lambda s: datetime.today() + timedelta(days=-365))
    date_filter_cmp = fields.Selection([('no_comparison', 'None'), ('previous_period', 'Previous Periods'),
                                        ('same_last_year', 'Same Last Year'), ('custom', 'Custom')],
                                       default='no_comparison', required=True)
    periods_number = fields.Integer('Number of periods', default=1)

    all_entries = fields.Boolean(string='Include Unposted Entries', default=False)
    operating_unit_ids = fields.Many2many('operating.unit', string='Operating Unit')
    cost_center_ids = fields.Many2many('account.cost.center', string='Cost Center')

    @api.constrains('date_from', 'date_to')
    def _check_date_range(self):
        if self.date_from > self.date_to and self.date_filter == 'custom':
            raise ValidationError(_("Start date must be less then End date!!"))

    @api.constrains('date_from_cmp', 'date_to_cmp')
    def _check_date_range_cmp(self):
        if self.date_from_cmp > self.date_to_cmp and self.date_filter_cmp == 'custom':
            raise ValidationError(_("Start date for comp. must be less then End date for comp.!!"))

    @api.constrains('periods_number')
    def _check_periods_number(self):
        if self.date_filter_cmp in ['previous_period', 'same_last_year']:
            if self.periods_number < 1 or self.periods_number > 5:
                raise ValidationError('Number of periods must be between 1 to 5!!')

    @api.depends('comparison')
    def _get_comparison(self):
        for rec in self:
            if rec.date_filter_cmp == 'no_comparison':
                rec.comparison = False
            else:
                rec.comparison = True

    @api.onchange('date_filter')
    def _onchange_date_filter(self):
        date_now = fields.Date.today()
        dt = fields.Date.from_string(date_now)

        if self.date_filter == 'this_month':
            self.date_from = dt.replace(day=1)
            _, last_day = calendar.monthrange(dt.year, dt.month)
            self.date_to = dt.replace(day=last_day)

        elif self.date_filter == 'this_quarter':
            quarter = (dt.month - 1) / 3 + 1
            if quarter == 4:
                self.date_from = dt.replace(month=10, day=1)
                self.date_to = dt.replace(month=12, day=31)

            elif quarter == 3:
                self.date_from = dt.replace(month=7, day=1)
                _, last_day = calendar.monthrange(dt.year, 9)
                self.date_to = dt.replace(month=9, day=last_day)

            elif quarter == 2:
                self.date_from = dt.replace(month=4, day=1)
                _, last_day = calendar.monthrange(dt.year, 6)
                self.date_to = dt.replace(month=6, day=last_day)

            else:
                self.date_from = dt.replace(month=1, day=1)
                _, last_day = calendar.monthrange(dt.year, 3)
                self.date_to = dt.replace(month=3, day=last_day)

        elif self.date_filter == 'this_year':
            self.date_from = dt.replace(month=1, day=1)
            self.date_to = dt.replace(month=12, day=31)

        elif self.date_filter == 'last_month':
            year, month = divmod(dt.year * 12 + 1, 12)
            if dt.month <= month:
                # year = dt.year - year - 1
                year = dt.year - 1
                month = dt.month - month + 12
            else:
                year = dt.year
                month = dt.month - month

            self.date_from = dt.replace(year=year, month=month, day=1)
            _, last_day = calendar.monthrange(year, month)
            self.date_to = dt.replace(year=year, month=month, day=last_day)

        elif self.date_filter == 'last_quarter':
            quarter = ((dt.month - 1) / 3 + 1) - 1
            if quarter < 1:
                year = dt.year - 1
                self.date_from = dt.replace(year=year, month=10, day=1)
                self.date_to = dt.replace(year=year, month=12, day=31)
            else:
                if quarter == 3:
                    self.date_from = dt.replace(month=7, day=1)
                    _, last_day = calendar.monthrange(dt.year, 9)
                    self.date_to = dt.replace(month=9, day=last_day)

                elif quarter == 2:
                    self.date_from = dt.replace(month=4, day=1)
                    _, last_day = calendar.monthrange(dt.year, 6)
                    self.date_to = dt.replace(month=6, day=last_day)

                else:
                    self.date_from = dt.replace(month=1, day=1)
                    _, last_day = calendar.monthrange(dt.year, 3)
                    self.date_to = dt.replace(month=3, day=last_day)

        elif self.date_filter == 'last_year':
            year = dt.year - 1
            self.date_from = dt.replace(year=year, month=1, day=1)
            self.date_to = dt.replace(year=year, month=12, day=31)

        else:
            self.date_from = dt.replace(day=1)
            _, last_day = calendar.monthrange(dt.year, dt.month)
            self.date_to = dt.replace(day=last_day)

    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        if self.date_filter_cmp == 'custom':
            if self.date_from == self.date_from_cmp and self.date_to == self.date_to_cmp:
                raise UserError(_('Comparison date range should be different.'))

        return self.env['report'].get_action(self, report_name='samuda_account_reports.profit_loss_with_realization_xlsx')

    def get_full_date_names(self, dt_to, dt_from=None):
        convert_date = self.env['ir.qweb.field.date'].value_to_html

        if self.date_filter_cmp == 'custom' and dt_from == self.date_from_cmp and dt_to == self.date_to_cmp:
            date_from = convert_date(dt_from, None)
            date_to = convert_date(dt_to, None)
            return (_('From %s to %s')) % (date_from, date_to)

        date_to = convert_date(dt_to, None)
        dt_to = datetime.strptime(dt_to, "%Y-%m-%d")

        if dt_from:
            date_from = convert_date(dt_from, None)
        if 'month' in self.date_filter:
            return '%s %s' % (self._get_month(dt_to.month - 1), dt_to.year)
        if 'quarter' in self.date_filter:
            month_start = self.env.user.company_id.fiscalyear_last_month + 1
            month = dt_to.month if dt_to.month >= month_start else dt_to.month + 12
            quarter = int((month - month_start) / 3) + 1
            return dt_to.strftime(_('Quarter #') + str(quarter) + ' %Y')
        if 'year' in self.date_filter:
            if self.env.user.company_id.fiscalyear_last_day == 31 and self.env.user.company_id.fiscalyear_last_month == 12:
                return "Year: " + dt_to.strftime('%Y')
            else:
                return str(dt_to.year - 1) + ' - ' + str(dt_to.year)
        if not dt_from:
            return _('As of %s') % (date_to,)
        return (_('From %s to %s')) % (date_from, date_to)

    def _get_month(self, index):
        return [
            _('January'), _('February'), _('March'), _('April'), _('May'), _('June'),
            _('July'), _('August'), _('September'), _('October'), _('November'), _('December')
        ][index]

    def get_periods(self):
        res = self.get_cmp_periods()
        res[:0] = [[self.date_from, self.date_to]]
        return res

    def get_cmp_periods(self):
        if not self.comparison:
            return []

        dt_to = datetime.strptime(self.date_to, "%Y-%m-%d")
        dt_from = self.date_from and datetime.strptime(self.date_from, "%Y-%m-%d") or self.env.user.company_id.compute_fiscalyear_dates(dt_to)['date_from']
        columns = []
        if self.date_filter_cmp == 'custom':
            return [[self.date_from_cmp, self.date_to_cmp]]

        if self.date_filter_cmp == 'same_last_year':
            columns = []
            for k in xrange(0, self.periods_number):
                dt_to -= timedelta(days=366 if calendar.isleap(dt_to.year) else 365)
                dt_from = dt_from.replace(year=dt_from.year - 1)
                columns += [[dt_from.strftime("%Y-%m-%d"), dt_to.strftime("%Y-%m-%d")]]

            return columns

        if 'month' in self.date_filter:
            for k in xrange(0, self.periods_number):
                dt_to = dt_to.replace(day=1)
                dt_to -= timedelta(days=1)
                dt_from -= timedelta(days=1)
                dt_from = dt_from.replace(day=1)
                columns += [[dt_from.strftime("%Y-%m-%d"), dt_to.strftime("%Y-%m-%d")]]

        elif 'quarter' in self.date_filter:
            for k in xrange(0, self.periods_number):
                if dt_to.month == 12:
                    dt_to = dt_to.replace(month=9, day=30)
                elif dt_to.month == 9:
                    dt_to = dt_to.replace(month=6, day=30)
                elif dt_to.month == 6:
                    dt_to = dt_to.replace(month=3, day=31)
                else:
                    dt_to = dt_to.replace(month=12, day=31, year=dt_to.year - 1)

                if dt_from.month == 10:
                    dt_from = dt_from.replace(month=7)
                elif dt_from.month == 7:
                    dt_from = dt_from.replace(month=4)
                elif dt_from.month == 4:
                    dt_from = dt_from.replace(month=1)
                else:
                    dt_from = dt_from.replace(month=10, year=dt_from.year - 1)
                columns += [[dt_from.strftime("%Y-%m-%d"), dt_to.strftime("%Y-%m-%d")]]

        elif 'year' in self.date_filter:
            dt_to = datetime.strptime(self.date_to, "%Y-%m-%d")
            for k in xrange(0, self.periods_number):
                dt_to = dt_to.replace(year=dt_to.year - 1)
                dt_from = dt_to.replace(year=dt_to.year - 1) + timedelta(days=1)
                columns += [[dt_from.strftime("%Y-%m-%d"), dt_to.strftime("%Y-%m-%d")]]

        else:
            dt_from = datetime.strptime(self.date_from, "%Y-%m-%d")
            delta = dt_to - dt_from
            delta = timedelta(days=delta.days + 1)

            # get the number of days in month from date_from
            number_of_days_in_month = calendar.monthrange(dt_from.year, dt_from.month)[1]

            if delta.days == number_of_days_in_month:
                for k in xrange(0, self.periods_number):
                    dt_to = dt_to.replace(day=1)
                    dt_to -= timedelta(days=1)
                    dt_from -= timedelta(days=1)
                    dt_from = dt_from.replace(day=1)
                    columns += [[dt_from.strftime("%Y-%m-%d"), dt_to.strftime("%Y-%m-%d")]]
            else:
                for k in xrange(0, self.periods_number):
                    dt_from -= delta
                    dt_to -= delta
                    columns += [[dt_from.strftime("%Y-%m-%d"), dt_to.strftime("%Y-%m-%d")]]

        return columns
