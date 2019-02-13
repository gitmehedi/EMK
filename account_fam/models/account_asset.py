# -*- coding: utf-8 -*-

import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import float_compare, float_is_zero


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'
    _order = 'id desc'

    asset_seq = fields.Char(string='Code', readonly=True)
    batch_no = fields.Char(string='Batch No', readonly=True)
    method_progress_factor = fields.Float('Depreciation Factor', default=0.2)
    is_custom_depr = fields.Boolean(default=True, required=True)
    depreciation_year = fields.Integer(string='Asset Life (In Year)', required=True, default=1)
    method = fields.Selection([('linear', 'Straight Line/Linear'), ('degressive', 'Reducing Method')],
                              string='Computation Method', required=True, default='linear',
                              help="Choose the method to use to compute the amount of depreciation lines.\n"
                                   "  * Linear: Calculated on basis of: Gross Value - Salvage Value/ Useful life of the fixed asset\n"
                                   "  * Reducing Method: Calculated on basis of: Residual Value * Depreciation Factor")
    receive_date = fields.Date(string='Receive Date')
    asset_usage_date = fields.Date(string='Allocation Date', help='Asset Allocation/Usage Date')
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', required=True)
    invoice_date = fields.Date(related='invoice_id.date', string='Invoice Date')
    method_period = fields.Integer(string='Number of Months in a Period', required=True, readonly=True, default=1,
                                   states={'draft': [('readonly', False)]})
    allocation_status = fields.Boolean(default=False, string='Allocation Status')
    value = fields.Float(string='Cost Value')
    value_residual = fields.Float(string='Book Value')

    @api.constrains('depreciation_year')
    def check_depreciation_year(self):
        if self.depreciation_year < 1:
            raise ValidationError(_('Total year cannot be zero or negative value.'))

    @api.onchange('depreciation_year')
    def onchange_depreciation_year(self):
        if self.depreciation_year:
            self.method_number = int(12 * self.depreciation_year)

    @api.multi
    def validate(self):
        super(AccountAssetAsset, self).validate()
        code = self.env['ir.sequence'].next_by_code('account.asset.asset.code') or _('New')
        self.write({'asset_seq': code})

    def depr_date_format(self, depreciation_date):
        no_of_days = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
        return depreciation_date.replace(day=no_of_days)

    @api.multi
    def compute_depreciation_board(self):
        if self.is_custom_depr:
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
                    if self.method == 'linear':
                        date_delta = (datetime.strptime(self.date, "%Y-%m-%d") + relativedelta(
                            years=self.depreciation_year) - datetime.strptime(self.date, "%Y-%m-%d"))
                        amount = self._compute_board_amount(sequence, residual_amount, amount_to_depr,
                                                            undone_dotation_number,
                                                            posted_depreciation_line_ids, date_delta.days,
                                                            depreciation_date)
                        amount = self.currency_id.round(amount)
                        if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                            continue

                        residual_amount -= amount
                        remaining_amount = residual_amount
                    elif self.method == 'degressive':
                        amount = self._compute_board_amount(sequence, residual_amount, amount_to_depr,
                                                            undone_dotation_number,
                                                            posted_depreciation_line_ids, total_days, depreciation_date)
                        amount = self.currency_id.round(amount)

                        if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                            continue

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
                        'remaining_value': abs(remaining_amount),
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
        else:
            return super(AccountAssetAsset, self).compute_depreciation_board()

    def _compute_board_amount(self, sequence, residual_amount, amount_to_depr, undone_dotation_number,
                              posted_depreciation_line_ids, total_days, depreciation_date):
        if self.is_custom_depr:

            amount = 0
            if self.method == 'linear':
                if self.prorata:
                    no_of_day = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
                    if sequence == 1:
                        days = no_of_day - datetime.strptime(self.date, "%Y-%m-%d").day
                        amount = (self.value_residual / total_days) * days
                    elif sequence == undone_dotation_number:
                        amount = residual_amount
                    else:
                        days = no_of_day
                        amount = (self.value_residual / total_days) * days
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
        else:
            return super(AccountAssetAsset, self)._compute_board_amount(self, sequence, residual_amount, amount_to_depr,
                                                                        undone_dotation_number,
                                                                        posted_depreciation_line_ids, total_days,
                                                                        depreciation_date)

    def onchange_category_id_values(self, category_id):
        if category_id:
            category = self.env['account.asset.category'].browse(category_id)
            return {
                'value': {
                    'method': category.method,
                    'method_number': category.method_number,
                    'method_time': category.method_time,
                    'method_period': category.method_period,
                    'method_progress_factor': category.method_progress_factor,
                    'method_end': category.method_end,
                    'prorata': category.prorata,
                    'depreciation_year': category.depreciation_year,
                }
            }


class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    line_type = fields.Selection([('depreciation', 'Depreciation'), ('sale', 'Sale'), ('dispose', 'Dispose')],
                                 default='depreciation', required=True, string="Line Type")

    @api.multi
    def create_move(self, post_move=True):
        created_moves = self.env['account.move']
        prec = self.env['decimal.precision'].precision_get('Account')
        for line in self:
            if line.move_id:
                raise UserError(_('This depreciation is already linked to a journal entry! Please post or delete it.'))
            category_id = line.asset_id.category_id
            depreciation_date = self.env.context.get(
                'depreciation_date') or line.depreciation_date or fields.Date.context_today(self)
            company_currency = line.asset_id.company_id.currency_id
            current_currency = line.asset_id.currency_id
            amount = current_currency.with_context(date=depreciation_date).compute(line.amount, company_currency)
            asset_name = line.asset_id.name + ' (%s/%s)' % (line.sequence, len(line.asset_id.depreciation_line_ids))

            if self.env.context.get('dispose'):
                move_vals = self.format_dispose_move(amount, asset_name, category_id, prec, line,
                                                     company_currency,
                                                     current_currency, depreciation_date)
                line.write({'line_type': 'dispose'})
            elif self.env.context.get('sale'):
                move_vals = self.format_sale_move(amount, asset_name, category_id, prec, line,
                                                  company_currency,
                                                  current_currency, depreciation_date)
                line.write({'line_type': 'sale'})
            else:
                move_vals = self.format_depreciation_move(amount, asset_name, category_id, prec, line,
                                                          company_currency,
                                                          current_currency, depreciation_date)
                line.write({'line_type': 'depreciation'})

            move = self.env['account.move'].create(move_vals)
            line.write({'move_id': move.id, 'move_check': True})
            created_moves |= move

        if post_move and created_moves:
            created_moves.filtered(
                lambda m: any(m.asset_depreciation_ids.mapped('asset_id.category_id.open_asset'))).post()
        return [x.id for x in created_moves]

    def format_dispose_move(self, amount, asset_name, category_id, prec, line, company_currency, current_currency,
                            depreciation_date):
        depr_credit = {
            'name': asset_name,
            'account_id': category_id.account_asset_id.id,
            'debit': 0.0,
            'credit': self.asset_id.value if float_compare(self.asset_id.value, 0.0,
                                                           precision_digits=prec) > 0 else 0.0,
            'journal_id': category_id.journal_id.id,
            'partner_id': line.asset_id.partner_id.id,
            'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'sale' else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
        }
        depr_debit_1 = {
            'name': asset_name,
            'account_id': category_id.account_depreciation_id.id,
            'credit': 0.0,
            'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'journal_id': category_id.journal_id.id,
            'partner_id': line.asset_id.partner_id.id,
            'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'purchase' else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and line.amount or 0.0,
        }
        depr_debit_2 = {
            'name': asset_name,
            'account_id': category_id.account_asset_loss_id.id,
            'debit': self.asset_id.value - amount if float_compare(self.asset_id.value - amount, 0.0,
                                                                   precision_digits=prec) > 0 else 0.0,
            'credit': 0.0,
            'journal_id': category_id.journal_id.id,
            'partner_id': line.asset_id.partner_id.id,
            'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'sale' else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
        }
        return {
            'ref': line.asset_id.code,
            'date': depreciation_date or False,
            'journal_id': category_id.journal_id.id,
            'line_ids': [(0, 0, depr_credit), (0, 0, depr_debit_1), (0, 0, depr_debit_2)],
        }

    def format_sale_move(self, amount, asset_name, category_id, prec, line, company_currency, current_currency,
                         depreciation_date):
        sale_id = self.env['account.asset.sale'].search([('name', '=', self.env.context.get('sale_id'))])
        sales = self.env['account.asset.sale.line'].search(
            [('sale_id', '=', sale_id.id), ('asset_id', '=', self.asset_id.id)])

        if sales.sale_value > amount:
            gain = sales.sale_value - amount
            loss_gain = {
                'name': asset_name,
                'account_id': category_id.account_asset_loss_id.id,
                'debit': 0.0,
                'credit': gain if float_compare(gain, 0.0, precision_digits=prec) > 0 else 0.0,
                'journal_id': category_id.journal_id.id,
                'partner_id': line.asset_id.partner_id.id,
                'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'sale' else False,
                'currency_id': company_currency != current_currency and current_currency.id or False,
                'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
            }
        else:
            loss = amount - sales.sale_value
            loss_gain = {
                'name': asset_name,
                'account_id': category_id.account_asset_loss_id.id,
                'debit': loss if float_compare(loss, 0.0, precision_digits=prec) > 0 else 0.0,
                'credit': 0.0,
                'journal_id': category_id.journal_id.id,
                'partner_id': line.asset_id.partner_id.id,
                'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'sale' else False,
                'currency_id': company_currency != current_currency and current_currency.id or False,
                'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
            }
        asset_credit = {
            'name': asset_name,
            'account_id': category_id.account_asset_id.id,
            'debit': 0.0,
            'credit': self.asset_id.value if float_compare(self.asset_id.value, 0.0,
                                                           precision_digits=prec) > 0 else 0.0,
            'journal_id': category_id.journal_id.id,
            'partner_id': line.asset_id.partner_id.id,
            'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'sale' else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
        }
        depr_debit = {
            'name': asset_name,
            'account_id': category_id.account_depreciation_id.id,
            'credit': 0.0,
            'debit': self.asset_id.value - amount if float_compare(self.asset_id.value - amount, 0.0,
                                                                   precision_digits=prec) > 0 else 0.0,
            'journal_id': category_id.journal_id.id,
            'partner_id': line.asset_id.partner_id.id,
            'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'purchase' else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and line.amount or 0.0,
        }

        sale_susp_debit = {
            'name': asset_name,
            'account_id': category_id.asset_sale_suspense_account_id.id,
            'debit': sales.sale_value if float_compare(sales.sale_value, 0.0, precision_digits=prec) > 0 else 0.0,
            'credit': 0.0,
            'journal_id': category_id.journal_id.id,
            'partner_id': line.asset_id.partner_id.id,
            'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'sale' else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
        }
        return {
            'ref': line.asset_id.code,
            'date': depreciation_date or False,
            'journal_id': category_id.journal_id.id,
            'line_ids': [(0, 0, asset_credit), (0, 0, depr_debit), (0, 0, loss_gain), (0, 0, sale_susp_debit)],
        }

    def format_depreciation_move(self, amount, asset_name, category_id, prec, line, company_currency,
                                 current_currency, depreciation_date):
        move_line_1 = {
            'name': asset_name,
            'account_id': category_id.account_depreciation_id.id,
            'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'journal_id': category_id.journal_id.id,
            'partner_id': line.asset_id.partner_id.id,
            'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'sale' else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
        }
        move_line_2 = {
            'name': asset_name,
            'account_id': category_id.account_depreciation_expense_id.id,
            'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'journal_id': category_id.journal_id.id,
            'partner_id': line.asset_id.partner_id.id,
            'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'purchase' else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and line.amount or 0.0,
        }
        return {
            'ref': line.asset_id.code,
            'date': depreciation_date or False,
            'journal_id': category_id.journal_id.id,
            'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
        }
