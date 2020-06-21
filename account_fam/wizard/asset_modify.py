# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning
from odoo.tools import float_compare, float_is_zero


class AssetModify(models.TransientModel):
    _inherit = 'asset.modify'

    method_number = fields.Integer(string='Asset Life (In Year)', required=True, default=0, invisible=True)
    method_progress_factor = fields.Float('Depreciation Factor', digits=(1,3), default=0.0)
    depreciation_year = fields.Integer(string='Asset Life (In Year)', required=True, default=0)
    adjusted_depr_amount = fields.Float(string='Adjusted Depr. Amount')
    method = fields.Selection([('degressive', 'Reducing Method'),
                               ('linear', 'Straight Line/ Linear')],
                              string='Computation Method', required=True, default='linear',
                              help="Choose the method to use to compute the amount of depreciation lines.\n"
                                   "  * Linear: Calculated on basis of: Gross Value - Salvage Value/ Useful life of the fixed asset\n"
                                   "  * Reducing Method: Calculated on basis of: Residual Value * Depreciation Factor")

    @api.constrains('method')
    def check_method(self):
        if self.method == 'linear':
            if self.depreciation_year < 1:
                raise ValidationError(_('Asset Life (In Year) cann\'t be zero or negative value.'))
        if self.method == 'degressive':
            if self.method_progress_factor <= 0:
                raise ValidationError(_('Depreciation Factor cann\'t be zero or negative value.'))

    @api.model
    def default_get(self, fields):
        res = super(AssetModify, self).default_get(fields)
        asset_id = self.env.context.get('active_id')
        asset = self.env['account.asset.asset'].browse(asset_id)

        if 'name' in fields:
            res.update({'name': asset.name})
        if 'method_number' in fields and asset.method_time == 'number':
            res.update({'method_number': asset.method_number})
        if 'method_period' in fields:
            res.update({'method_period': asset.method_period})
        if 'method_end' in fields and asset.method_time == 'end':
            res.update({'method_end': asset.method_end})
        if 'method' in fields:
            res.update({'method': asset.method})
        if 'method_progress_factor' in fields:
            res.update({'method_progress_factor': asset.method_progress_factor})
        if 'depreciation_year' in fields:
            res.update({'depreciation_year': asset.depreciation_year})
        if self.env.context.get('active_id'):
            active_asset = self.env['account.asset.asset'].browse(self.env.context.get('active_id'))
            res['asset_method_time'] = active_asset.method_time
        return res

    @api.multi
    def modify(self):
        """ Modifies the duration of asset for calculating depreciation
        and maintains the history of old values, in the chatter.
        """
        for rec in self._context['active_ids']:
            asset = self.env['account.asset.asset'].browse(rec)
            if asset.state == 'open' and not asset.depreciation_flag:
                old_values = {
                    'method_number': asset.method_number,
                    'method_period': asset.method_period,
                    'method_end': asset.method_end,
                    'method_progress_factor': asset.method_progress_factor,
                    'depreciation_year': asset.depreciation_year,
                    'method': asset.method,
                }
                asset_vals = {
                    'method_number': self.method_number,
                    'method_period': self.method_period,
                    'method_end': self.method_end,
                    'method_progress_factor': self.method_progress_factor,
                    'depreciation_year': self.depreciation_year,
                    'method': self.method,
                }
                asset.write(asset_vals)

                tracked_fields = self.env['account.asset.asset'].fields_get(
                    ['method_number', 'method_period', 'method_end'])
                changes, tracking_value_ids = asset._message_track(tracked_fields, old_values)
                if changes:
                    asset.message_post(subject=_('Depreciation board modified'), body=self.name,
                                       tracking_value_ids=tracking_value_ids)
                if self.adjusted_depr_amount > 0 and asset.allocation_status == True:
                    depr_value = self.adjusted_depr_amount
                    depreciated_amount = sum([rec.amount for rec in asset.depreciation_line_ids]) + depr_value
                    remaining_value = asset.value - depreciated_amount
                    vals = {
                        'amount': depr_value,
                        'asset_id': asset.id,
                        'sequence': 1,
                        'name': asset.code or '/',
                        'remaining_value': abs(remaining_value),
                        'depreciated_value': depreciated_amount,
                        'depreciation_date': fields.Datetime.now(),
                        'days': 0,
                        'asset_id': asset.id,
                    }

                    line = asset.depreciation_line_ids.create(vals)
                    if line:
                        move = self.create_move(asset, depr_value)
                        line.write({'move_id': move.id, 'move_check': True})
                        if move.state == 'draft' and line.move_id.id == move.id:
                            move.sudo().post()
            else:
                flag = 'Active' if asset.depreciation_flag else 'In-Active'
                raise Warning(_('Depreciation of Asset {0} is in Status [{1}] with Awaiting Disposal [{2}]'.format(
                    asset.display_name,
                    asset.state, flag)))

        return {'type': 'ir.actions.act_window_close'}

    def create_move(self, asset, depr_value):
        prec = self.env['decimal.precision'].precision_get('Account')
        company_currency = asset.company_id.currency_id
        current_currency = asset.currency_id
        sub_operating_unit = asset.sub_operating_unit_id.id if asset.sub_operating_unit_id else None
        credit = {
            'name': asset.display_name,
            'account_id': asset.asset_type_id.account_depreciation_id.id,
            'debit': 0.0,
            'credit': depr_value if float_compare(depr_value, 0.0,
                                                  precision_digits=prec) > 0 else 0.0,
            'journal_id': asset.category_id.journal_id.id,
            'operating_unit_id': asset.current_branch_id.id,
            'sub_operating_unit_id': sub_operating_unit,
            'analytic_account_id': asset.cost_centre_id.id if asset.cost_centre_id else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
        }
        debit = {
            'name': asset.display_name,
            'account_id': asset.asset_type_id.account_depreciation_expense_id.id,
            'debit': depr_value if float_compare(depr_value, 0.0,
                                                 precision_digits=prec) > 0 else 0.0,
            'credit': 0.0,
            'journal_id': asset.category_id.journal_id.id,
            'operating_unit_id': asset.current_branch_id.id,
            'sub_operating_unit_id': sub_operating_unit,
            'analytic_account_id': asset.cost_centre_id.id,
            'currency_id': company_currency != current_currency and current_currency.id or False,
        }

        return self.env['account.move'].create({
            'ref': asset.code,
            'date': fields.Datetime.now() or False,
            'journal_id': asset.category_id.journal_id.id,
            'operating_unit_id': asset.current_branch_id.id,
            'sub_operating_unit_id': sub_operating_unit,
            'line_ids': [(0, 0, debit), (0, 0, credit)],
        })
