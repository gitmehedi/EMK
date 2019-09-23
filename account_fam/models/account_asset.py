# -*- coding: utf-8 -*-

import calendar
from datetime import datetime
from datetime import date as DT
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare, float_is_zero

DATE_FORMAT = "%Y-%m-%d"


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'
    _order = "asset_seq desc"

    name = fields.Char(string='Asset Name', required=True, readonly=True, states={'close': [('readonly', False)]})
    category_id = fields.Many2one(string='Asset Type', required=True, change_default=True, readonly=True)
    asset_type_id = fields.Many2one(string='Asset Category', required=True, change_default=True, readonly=True)
    asset_seq = fields.Char(string='Asset Code', readonly=True, track_visibility='onchange')
    batch_no = fields.Char(string='Batch No', readonly=True,
                           track_visibility='onchange', states={'draft': [('readonly', False)]})
    method_progress_factor = fields.Float('Depreciation Factor', default=0.2, track_visibility='onchange')
    is_custom_depr = fields.Boolean(default=True, required=True, track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string="Vendor", track_visibility='onchange')
    depreciation_year = fields.Integer(string='Asset Life (In Year)', required=True, default=1,
                                       track_visibility='onchange')
    method = fields.Selection([('degressive', 'Reducing Method'), ('linear', 'Straight Line/Linear')],
                              track_visibility='onchange',
                              string='Computation Method', required=True, default='degressive',
                              help="Choose the method to use to compute the amount of depreciation lines.\n"
                                   "  * Linear: Calculated on basis of: Gross Value - Salvage Value/ Useful life of the fixed asset\n"
                                   "  * Reducing Method: Calculated on basis of: Residual Value * Depreciation Factor")
    warranty_date = fields.Date(string='Warranty Date', track_visibility='onchange', readonly=True,
                                states={'draft': [('readonly', False)]})
    date = fields.Date(string='Purchase Date', track_visibility='onchange')
    asset_usage_date = fields.Date(string='Usage Date', help='Usage Date/Allocation Date', readonly=True,
                                   track_visibility='onchange', states={'draft': [('readonly', False)]})
    model_name = fields.Char(string='Model', track_visibility='onchange', readonly=True,
                             states={'draft': [('readonly', False)]})
    operating_unit_id = fields.Many2one('operating.unit', string='Purchase Branch', required=True,
                                        track_visibility='onchange')
    invoice_date = fields.Date(related='invoice_id.date', string='Bill Date', track_visibility='onchange')
    method_period = fields.Integer(string='One Entry (In Month)', required=True, readonly=True, default=1,
                                   states={'draft': [('readonly', False)]}, track_visibility='onchange')
    value = fields.Float(string='Cost Value', track_visibility='onchange', readonly=True)
    value_residual = fields.Float(string='WDV', track_visibility='onchange')
    advance_amount = fields.Float(string='Adjusted Amount', track_visibility='onchange', readonly=True,
                                  states={'draft': [('readonly', False)]})
    current_branch_id = fields.Many2one('operating.unit', string='Current Branch', required=True,
                                        track_visibility='onchange')
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Sub Operating Unit',
                                            track_visibility='onchange', readonly=True,
                                            states={'draft': [('readonly', False)]})
    accumulated_value = fields.Float(string='Accumulated Depreciation', compute="_compute_accumulated_value",
                                     track_visibility='onchange', readonly=True,
                                     states={'draft': [('readonly', False)]})
    asset_description = fields.Text(string='Asset Description', readonly=True, states={'draft': [('readonly', False)]})
    cost_centre_id = fields.Many2one('account.analytic.account', string='Cost Centre',
                                     track_visibility='onchange', readonly=True,
                                     states={'draft': [('readonly', False)]})
    note = fields.Text(string="Note", required=False, readonly=True, states={'draft': [('readonly', False)]})
    allocation_status = fields.Boolean(string='Allocation Status', track_visibility='onchange', default=False)
    depreciation_flag = fields.Boolean(string='Depreciation Flag', track_visibility='onchange', default=False)
    lst_depr_date = fields.Date(string='Last Depr. Date', readonly=True, track_visibility='onchange')

    @api.model
    def create(self, vals):
        asset = super(AccountAssetAsset, self).create(vals)
        return asset

    @api.multi
    def write(self, vals):
        res = super(AccountAssetAsset, self).write(vals)
        return res

    @api.constrains('depreciation_year')
    def check_depreciation_year(self):
        if self.depreciation_year < 1:
            raise ValidationError(_('Total year cannot be zero or negative value.'))

    @api.onchange('depreciation_year')
    def onchange_depreciation_year(self):
        if self.depreciation_year:
            self.method_number = int(12 * self.depreciation_year)

    @api.one
    @api.depends('value', 'salvage_value', 'depreciation_line_ids.move_check', 'depreciation_line_ids.amount')
    def _compute_accumulated_value(self):
        self.accumulated_value = self.value - self.value_residual

    @api.onchange("name")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()

    @api.multi
    def all_asset_validate(self):
        assets = self.search([('state', '=', 'open')])
        for asset in assets:
            asset.validate()

    @api.multi
    def validate(self):
        super(AccountAssetAsset, self).validate()
        if not self.asset_seq:
            code = self.env['ir.sequence'].next_by_code('account.asset.asset.code') or _('New')
            ATAC = '{0}-{1}'.format(self.category_id.code, self.asset_type_id.code)
            self.write({'asset_seq': code.replace('ATAC', ATAC)})

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = record.name
            if record.asset_seq:
                name = '[' + record.asset_seq + '] ' + record.name
            result.append((record.id, name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        names1 = super(models.Model, self).name_search(name=name, args=args, operator=operator, limit=limit)
        names2 = []
        if name:
            domain = [('name', '=ilike', name + '%')]
            names2 = self.search(domain, limit=limit).name_get()
        return list(set(names1) | set(names2))[:limit]

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'open')]

    @api.multi
    def compute_depreciation_board(self):
        return False

    def _compute_board_amount(self, sequence, residual_amount, amount_to_depr, undone_dotation_number,
                              posted_depreciation_line_ids, total_days, depreciation_date):
        if self.is_custom_depr:
            amount, days = 0, 0
            if self.method == 'linear':
                if self.prorata:
                    no_of_day = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
                    if sequence == 1:
                        days = (self.date_str_format(str(depreciation_date)) - self.date_str_format(
                            self.asset_usage_date)).days
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

            return (amount, days)
        else:
            return super(AccountAssetAsset, self)._compute_board_amount(self, sequence, residual_amount, amount_to_depr,
                                                                        undone_dotation_number,
                                                                        posted_depreciation_line_ids, total_days,
                                                                        depreciation_date)

    @api.multi
    def _get_last_depreciation_date(self):
        """
        @param id: ids of a account.asset.asset objects
        @return: Returns a dictionary of the effective dates of the last depreciation entry made for given asset ids. If there isn't any, return the purchase date of this asset
        """
        self.env.cr.execute("""
                SELECT a.id as id, COALESCE(MAX(m.date),a.asset_usage_date) AS date
                FROM account_asset_asset a
                LEFT JOIN account_asset_depreciation_line rel ON (rel.asset_id = a.id)
                LEFT JOIN account_move m ON (rel.move_id = m.id)
                WHERE a.id IN %s
                GROUP BY a.id, m.date """, (tuple(self.ids),))
        result = dict(self.env.cr.fetchall())
        return result

    @api.model
    def _cron_generate_entries(self):
        date = datetime.today()
        ungrouped_assets = self.env['account.asset.asset'].search(
            [('state', '=', 'open'), ('category_id.group_entries', '=', False)])
        for asset in ungrouped_assets:
            self.compute_depreciation_history(date, asset)

    @api.model
    def compute_depreciation_history(self, date, asset):

        if asset.allocation_status and asset.state == 'open' and not asset.depreciation_flag:
            last_depr_date = asset._get_last_depreciation_date()
            curr_date = date
            curr_depr_date = self.date_depr_format(curr_date)

            if asset.method == 'linear':
                date_delta = (self.date_str_format(asset.date) + relativedelta(
                    years=asset.depreciation_year) - self.date_str_format(asset.date)).days
                daily_depr = (asset.value - asset.salvage_value) / date_delta
            elif asset.method == 'degressive':
                year = self.date_str_format(asset.date).year
                date_delta = (DT(year, 12, 31) - DT(year, 01, 01)).days + 1
                daily_depr = ((asset.value - asset.salvage_value) * asset.method_progress_factor) / date_delta

            if not asset.depreciation_line_ids:
                no_of_days = (curr_depr_date - self.date_str_format(last_depr_date[asset['id']])).days
                depr_amount = no_of_days * daily_depr
                cumul_depr = depr_amount
                book_val_amount = asset.value_residual - cumul_depr
            else:
                no_of_days = curr_depr_date.day
                depr_amount = no_of_days * daily_depr
                cumul_depr = depr_amount
                book_val_amount = asset.value_residual - cumul_depr

            vals = {
                'amount': depr_amount,
                'asset_id': self.id,
                'sequence': 1,
                'name': (asset.code or '') + '/' + str(1),
                'remaining_value': abs(book_val_amount),
                'depreciated_value': depr_amount,
                'depreciation_date': curr_depr_date.date(),
                'days': no_of_days,
                'asset_id': asset.id,
            }

            rec = asset.depreciation_line_ids.search(
                [('asset_id', '=', vals['asset_id']), ('depreciation_date', '=', curr_depr_date.date())])
            if not rec:
                depreciation = asset.depreciation_line_ids.create(vals)
                if depreciation:
                    asset.create_move(depreciation)
                    asset.write({'lst_depr_date': curr_depr_date.date()})

    @api.multi
    def create_move(self, line):
        created_moves = self.env['account.move']
        prec = self.env['decimal.precision'].precision_get('Account')
        if line:
            if line.move_id:
                raise UserError(_('This depreciation is already linked to a journal entry! Please post or delete it.'))
            category_id = line.asset_id.category_id
            depreciation_date = self.env.context.get(
                'depreciation_date') or line.depreciation_date or fields.Date.context_today(self)
            company_currency = line.asset_id.company_id.currency_id
            current_currency = line.asset_id.currency_id
            amount = current_currency.with_context(date=depreciation_date).compute(line.amount, company_currency)
            asset_name = line.asset_id.name + ' (%s/%s)' % (line.sequence, len(line.asset_id.depreciation_line_ids))
            move_line_1 = {
                'name': asset_name,
                'account_id': category_id.account_depreciation_id.id,
                'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                'journal_id': category_id.journal_id.id if category_id.journal_id else False,
                'partner_id': line.asset_id.partner_id.id if line.asset_id.partner_id else False,
                'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'sale' else False,
                'currency_id': company_currency != current_currency and current_currency.id or False,
                'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
            }
            move_line_2 = {
                'name': asset_name,
                'account_id': category_id.account_depreciation_expense_id.id,
                'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                'journal_id': category_id.journal_id.id if category_id.journal_id else False,
                'partner_id': line.asset_id.partner_id.id if line.asset_id.partner_id else False,
                'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'purchase' else False,
                'currency_id': company_currency != current_currency and current_currency.id or False,
                'amount_currency': company_currency != current_currency and line.amount or 0.0,
            }
            move_vals = {
                'ref': line.asset_id.code,
                'date': depreciation_date or False,
                'journal_id': category_id.journal_id.id,
                'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
            }
            move = self.env['account.move'].create(move_vals)
            line.write({'move_id': move.id, 'move_check': True})
            created_moves |= move

        if move.state == 'draft' and line.move_id.id == move.id:
            move.post()
            return True

    @api.multi
    def _compute_entries(self, date, group_entries=False):
        depreciation_ids = self.env['account.asset.depreciation.line'].search([
            ('asset_id', 'in', self.ids), ('depreciation_date', '<=', date),
            ('move_check', '=', False), ('active', '=', False)])
        if group_entries:
            return depreciation_ids.create_grouped_move()
        return depreciation_ids.create_move()

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

    def date_depr_format(self, date):
        no_of_days = calendar.monthrange(date.year, date.month)[1]
        return date.replace(day=no_of_days)

    def date_str_format(self, date):
        if type(date) is str:
            return datetime.strptime(date, DATE_FORMAT)
        elif type(date) is datetime:
            return "{0}-{1}-{2}".format(date.year, date.month, date.day)


class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    days = fields.Integer(string='Days', required=True)
    line_type = fields.Selection([('depreciation', 'Depreciation'), ('sale', 'Sale'), ('dispose', 'Dispose')],
                                 default='depreciation', required=True, string="Line Type")
    amount = fields.Float(string='Depreciation')
    remaining_value = fields.Float(string='WDV at Date')
    depreciation_date = fields.Date('Date')

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
            current_branch = line.asset_id.current_branch_id

            if self.env.context.get('dispose'):
                move_vals = self.format_dispose_move(amount, asset_name, category_id, prec, line,
                                                     company_currency,
                                                     current_currency, depreciation_date, current_branch)
                line.write({'line_type': 'dispose'})
            elif self.env.context.get('sale'):
                move_vals = self.format_sale_move(amount, asset_name, category_id, prec, line,
                                                  company_currency,
                                                  current_currency, depreciation_date, current_branch)
                line.write({'line_type': 'sale'})
            else:
                move_vals = self.format_depreciation_move(amount, asset_name, category_id, prec, line,
                                                          company_currency,
                                                          current_currency, depreciation_date, current_branch)
                line.write({'line_type': 'depreciation'})

            move = self.env['account.move'].create(move_vals)
            line.write({'move_id': move.id, 'move_check': True, 'active': True})
            created_moves |= move

        if post_move and created_moves:
            created_moves.filtered(
                lambda m: any(m.asset_depreciation_ids.mapped('asset_id.category_id.open_asset'))).post()
        return [x.id for x in created_moves]

    def format_dispose_move(self, amount, asset_name, category_id, prec, line, company_currency, current_currency,
                            depreciation_date, current_branch):
        depr_credit = {
            'name': asset_name,
            'account_id': category_id.account_asset_id.id,
            'debit': 0.0,
            'credit': self.asset_id.value if float_compare(self.asset_id.value, 0.0,
                                                           precision_digits=prec) > 0 else 0.0,
            'journal_id': category_id.journal_id.id if category_id.journal_id else False,
            'partner_id': line.asset_id.partner_id.id if line.asset_id.partner_id else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
        }
        depr_debit_1 = {
            'name': asset_name,
            'account_id': category_id.account_depreciation_id.id,
            'credit': 0.0,
            'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'journal_id': category_id.journal_id.id if category_id.journal_id else False,
            'partner_id': line.asset_id.partner_id.id if line.asset_id.partner_id else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and line.amount or 0.0,
        }
        depr_debit_2 = {
            'name': asset_name,
            'account_id': category_id.account_asset_loss_id.id,
            'debit': self.asset_id.value - amount if float_compare(self.asset_id.value - amount, 0.0,
                                                                   precision_digits=prec) > 0 else 0.0,
            'credit': 0.0,
            'journal_id': category_id.journal_id.id if category_id.journal_id else False,
            'partner_id': line.asset_id.partner_id.id if line.asset_id.partner_id else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
        }
        return {
            'ref': line.asset_id.code,
            'date': depreciation_date or False,
            'journal_id': category_id.journal_id.id,
            'operating_unit_id': current_branch.id,
            'line_ids': [(0, 0, depr_credit), (0, 0, depr_debit_1), (0, 0, depr_debit_2)],
        }

    def format_sale_move(self, amount, asset_name, category_id, prec, line, company_currency, current_currency,
                         depreciation_date, current_branch):
        sale_id = self.env['account.asset.sale'].search([('name', '=', self.env.context.get('sale_id'))])
        sales = self.env['account.asset.sale.line'].search(
            [('sale_id', '=', sale_id.id), ('asset_id', '=', self.asset_id.id)])

        if sales.sale_value > amount:
            gain = sales.sale_value - amount
            loss_gain = {
                'name': asset_name,
                'account_id': category_id.account_asset_gain_id.id,
                'debit': 0.0,
                'credit': gain if float_compare(gain, 0.0, precision_digits=prec) > 0 else 0.0,
                'journal_id': category_id.journal_id.id if category_id.journal_id else False,
                'partner_id': line.asset_id.partner_id.id if line.asset_id.partner_id else False,
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
                'journal_id': category_id.journal_id.id if category_id.journal_id else False,
                'partner_id': line.asset_id.partner_id.id if line.asset_id.partner_id else False,
                'currency_id': company_currency != current_currency and current_currency.id or False,
                'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
            }
        asset_credit = {
            'name': asset_name,
            'account_id': category_id.account_asset_id.id,
            'debit': 0.0,
            'credit': self.asset_id.value if float_compare(self.asset_id.value, 0.0,
                                                           precision_digits=prec) > 0 else 0.0,
            'journal_id': category_id.journal_id.id if category_id.journal_id else False,
            'partner_id': line.asset_id.partner_id.id if line.asset_id.partner_id else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
        }
        depr_debit = {
            'name': asset_name,
            'account_id': category_id.account_depreciation_id.id,
            'credit': 0.0,
            'debit': self.asset_id.value - amount if float_compare(self.asset_id.value - amount, 0.0,
                                                                   precision_digits=prec) > 0 else 0.0,
            'journal_id': category_id.journal_id.id if category_id.journal_id else False,
            'partner_id': line.asset_id.partner_id.id if line.asset_id.partner_id else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and line.amount or 0.0,
        }

        sale_susp_debit = {
            'name': asset_name,
            'account_id': category_id.asset_sale_suspense_account_id.id,
            'debit': sales.sale_value if float_compare(sales.sale_value, 0.0, precision_digits=prec) > 0 else 0.0,
            'credit': 0.0,
            'journal_id': category_id.journal_id.id if category_id.journal_id else False,
            'partner_id': line.asset_id.partner_id.id if line.asset_id.partner_id else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
        }
        return {
            'ref': line.asset_id.code,
            'date': depreciation_date or False,
            'journal_id': category_id.journal_id.id,
            'operating_unit_id': current_branch.id,
            'line_ids': [(0, 0, asset_credit), (0, 0, depr_debit), (0, 0, loss_gain), (0, 0, sale_susp_debit)],
        }

    def format_depreciation_move(self, amount, asset_name, category_id, prec, line, company_currency,
                                 current_currency, depreciation_date, current_branch):
        move_line_1 = {
            'name': asset_name,
            'account_id': category_id.account_depreciation_id.id,
            'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'journal_id': category_id.journal_id.id if category_id.journal_id else False,
            'partner_id': line.asset_id.partner_id.id if line.asset_id.partner_id else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
        }
        move_line_2 = {
            'name': asset_name,
            'account_id': category_id.account_depreciation_expense_id.id,
            'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'journal_id': category_id.journal_id.id if category_id.journal_id else False,
            'partner_id': line.asset_id.partner_id.id if line.asset_id.partner_id else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and line.amount or 0.0,
        }
        return {
            'ref': line.asset_id.code,
            'date': depreciation_date or False,
            'journal_id': category_id.journal_id.id,
            'operating_unit_id': current_branch.id,
            'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
        }
