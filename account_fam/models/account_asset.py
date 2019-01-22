# -*- coding: utf-8 -*-

import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import float_compare, float_is_zero


class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    category_ids = fields.One2many('account.asset.category', 'parent_type_id', string="Category")
    parent_type_id = fields.Many2one('account.asset.category', string="Asset Type", ondelete="restrict")

    @api.one
    def unlink(self):
        if self.category_ids:
            raise ValidationError(_("Please delete all asset category related with it."))
        return super(AccountAssetCategory, self).unlink()

    @api.constrains('name', 'parent_type_id')
    def _check_unique_name(self):
        if self.name:
            parent_type, msg = None, ''

            if self.parent_type_id:
                parent_type = self.parent_type_id.id
                msg = 'Asset Category already exists, Please choose another.'
            else:
                msg = 'Asset Type already exists, Please choose another.'

            name = self.search([('name', '=ilike', self.name), ('parent_type_id', '=', parent_type)])
            if len(name) > 1:
                raise ValidationError(_(msg))


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'
    _order = 'id desc'

    method_progress_factor = fields.Float('Depreciation Factor', default=0.2)
    depreciation_year = fields.Integer(string='Total Year', required=True)
    method = fields.Selection([('linear', 'Straight Line/ Linear'), ('degressive', 'Reducing Method')],
                              string='Computation Method', required=True, default='linear',
                              help="Choose the method to use to compute the amount of depreciation lines.\n"
                                   "  * Linear: Calculated on basis of: Gross Value - Salvage Value/ Useful life of the fixed asset\n"
                                   "  * Reducing Method: Calculated on basis of: Residual Value * Depreciation Factor")
    receive_date = fields.Date(string='Receive Date')
    asset_usage_date = fields.Date(string='Allocation Date', help='Asset Allocation/Usage Date')
    asset_type_id = fields.Many2one('account.asset.category', string='Asset Type', required=True, change_default=True,
                                    readonly=True, states={'draft': [('readonly', False)]})
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', required=True)
    invoice_date = fields.Date(related='invoice_id.date', string='Invoice Date')

    @api.onchange('category_id')
    def onchange_asset_category(self):
        if self.category_id:
            self.asset_type_id = None
            category_ids = self.env['account.asset.category'].search(
                [('parent_type_id', '=', self.category_id.id)])
            return {
                'domain': {'asset_type_id': [('id', 'in', category_ids.ids)]}
            }

    @api.onchange('depreciation_year')
    def onchange_depreciation_year(self):
        if self.depreciation_year:
            self.method_number = int(12 * self.depreciation_year)

    def depr_date_format(self, depreciation_date):
        no_of_days = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
        return depreciation_date.replace(day=no_of_days)

    @api.multi
    def compute_depreciation_board(self):
        self.ensure_one()

        posted_depreciation_line_ids = self.depreciation_line_ids.filtered(lambda x: x.move_check).sorted(
            key=lambda l: l.depreciation_date)
        unposted_depreciation_line_ids = self.depreciation_line_ids.filtered(lambda x: not x.move_check)

        # Remove old unposted depreciation lines. We cannot use unlink() with One2many field
        commands = [(2, line_id.id, False) for line_id in unposted_depreciation_line_ids]

        if self.value_residual != 0.0:
            amount_to_depr = residual_amount = self.value_residual
            if self.prorata:
                # if we already have some previous validated entries, starting date is last entry + method perio
                if posted_depreciation_line_ids and posted_depreciation_line_ids[-1].depreciation_date:
                    last_depreciation_date = datetime.strptime(posted_depreciation_line_ids[-1].depreciation_date,
                                                               DF).date()
                    depreciation_date = last_depreciation_date + relativedelta(months=+self.method_period)
                else:
                    depreciation_date = datetime.strptime(self._get_last_depreciation_date()[self.id], DF).date()
            else:
                # depreciation_date = 1st of January of purchase year if annual valuation, 1st of
                # purchase month in other cases
                if self.method_period >= 12:
                    if self.company_id.fiscalyear_last_month:
                        asset_date = date(year=int(self.date[:4]),
                                          month=self.company_id.fiscalyear_last_month,
                                          day=self.company_id.fiscalyear_last_day) + \
                                     relativedelta(days=1) + \
                                     relativedelta(year=int(self.date[:4]))  # e.g. 2018-12-31 +1 -> 2019
                    else:
                        asset_date = datetime.strptime(self.date[:4] + '-01-01', DF).date()
                else:
                    asset_date = datetime.strptime(self.date[:7] + '-01', DF).date()
                # if we already have some previous validated entries, starting date isn't 1st January but last entry + method period
                if posted_depreciation_line_ids and posted_depreciation_line_ids[-1].depreciation_date:
                    last_depreciation_date = datetime.strptime(posted_depreciation_line_ids[-1].depreciation_date,
                                                               DF).date()
                    depreciation_date = last_depreciation_date + relativedelta(months=+self.method_period)
                else:
                    depreciation_date = asset_date

            depreciation_date = self.depr_date_format(depreciation_date)
            day = depreciation_date.day
            month = depreciation_date.month
            year = depreciation_date.year
            total_days = (year % 4) and 365 or 366

            undone_dotation_number = self._compute_board_undone_dotation_nb(depreciation_date, total_days)
            year_date = depreciation_date.year
            year_amount = 0
            remaining_amount = residual_amount
            for x in range(len(posted_depreciation_line_ids), undone_dotation_number):

                sequence = x + 1
                amount = self._compute_board_amount(sequence, residual_amount, amount_to_depr, undone_dotation_number,
                                                    posted_depreciation_line_ids, total_days, depreciation_date)
                amount = self.currency_id.round(amount)

                if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                    continue

                if self.method == 'linear':
                    residual_amount -= amount
                    remaining_amount = residual_amount
                elif self.method == 'degressive':
                    next_year = depreciation_date + relativedelta(days=1)
                    remaining_amount = remaining_amount - amount
                    year_amount = year_amount + amount
                    if year_date != next_year.year:
                        year_date = next_year.year
                        residual_amount -= year_amount
                        year_amount = 0
                    else:
                        residual_amount = residual_amount

                vals = {
                    'amount': amount,
                    'asset_id': self.id,
                    'sequence': sequence,
                    'name': (self.code or '') + '/' + str(sequence),
                    'remaining_value': remaining_amount,
                    'depreciated_value': self.value - (self.salvage_value + remaining_amount),
                    'depreciation_date': depreciation_date.strftime(DF),
                }
                commands.append((0, False, vals))
                # Considering Depr. Period as months
                depreciation_date = date(year, month, day) + relativedelta(months=+self.method_period)
                depreciation_date = self.depr_date_format(depreciation_date)
                day = depreciation_date.day
                month = depreciation_date.month
                year = depreciation_date.year

        self.write({'depreciation_line_ids': commands})

        return True

    def _compute_board_amount(self, sequence, residual_amount, amount_to_depr, undone_dotation_number,
                              posted_depreciation_line_ids, total_days, depreciation_date):
        amount = 0
        if self.method == 'linear':
            no_of_day = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
            res_of_date = no_of_day - int(self.date[len(self.date) - 2:]) + 1
            amount = (amount_to_depr / (undone_dotation_number - len(posted_depreciation_line_ids)) /
                      no_of_day) * res_of_date

            if self.prorata:
                amount = amount_to_depr / self.method_number
                if sequence == 1:
                    if self.method_period % 12 != 0:
                        date = datetime.strptime(self.date, '%Y-%m-%d')
                        month_days = calendar.monthrange(date.year, date.month)[1]
                        days = month_days - date.day + 1
                        amount = (amount_to_depr / self.method_number) / month_days * days
                    else:
                        days = (self.company_id.compute_fiscalyear_dates(depreciation_date)[
                                    'date_to'] - depreciation_date).days + 1
                        amount = (amount_to_depr / self.method_number) / total_days * days
        elif self.method == 'degressive':
            if self.prorata:
                if sequence == 1:
                    if self.method_period % 12 != 0:
                        date = datetime.strptime(self.date, '%Y-%m-%d')
                        month_days = calendar.monthrange(date.year, date.month)[1]
                        days = month_days - date.day
                        amount = (residual_amount * self.method_progress_factor) / total_days * days
                    else:
                        days = (self.company_id.compute_fiscalyear_dates(depreciation_date)[
                                    'date_to'] - depreciation_date).days + 1
                        amount = (residual_amount * self.method_progress_factor) / total_days * days
                else:
                    month_days = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
                    amount = (residual_amount * self.method_progress_factor) / total_days * month_days

        return amount
