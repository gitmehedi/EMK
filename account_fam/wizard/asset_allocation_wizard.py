# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning
from odoo.tools import float_compare, float_is_zero


class AssetAllocationWizard(models.TransientModel):
    _name = 'asset.allocation.wizard'

    def default_from_branch(self):
        asset_id = self.env.context.get('active_id', False)
        asset = self.env['account.asset.asset'].browse(asset_id)
        if not asset.asset_allocation_ids:
            return asset.operating_unit_id
        else:
            branch = asset.asset_allocation_ids.search([('asset_id', '=', asset_id), ('state', '=', 'active')], limit=1)
            return branch.operating_unit_id

    def default_date(self):
        asset_id = self.env.context.get('active_id', False)
        asset = self.env['account.asset.asset'].browse(asset_id)
        if asset.asset_usage_date and len(asset.asset_allocation_ids.ids) == 0:
            return asset.asset_usage_date
        else:
            return fields.Datetime.now()

    asset_user = fields.Char("Asset User")
    date = fields.Date(string='Allocation/Transfer Date', required=True, default=default_date)
    operating_unit_id = fields.Many2one('operating.unit', string='From Branch', readonly=True,
                                        default=default_from_branch)
    to_operating_unit_id = fields.Many2one('operating.unit', string='To Branch', required=True)
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Sub Operating Unit')
    cost_centre_id = fields.Many2one('account.analytic.account', string='Cost Centre')

    @api.onchange('to_operating_unit_id')
    def onchange_operating_unit(self):
        if self.operating_unit_id:
            res = {}
            self.sub_operating_unit_id = 0
            sub_operating = self.env['sub.operating.unit'].search(
                [('operating_unit_id', '=', self.to_operating_unit_id.id)])
            res['domain'] = {
                'sub_operating_unit_id': [('id', 'in', sub_operating.ids)]
            }
            return res

    @api.multi
    def allocation(self):
        for rec in self._context['active_ids']:
            asset = self.env['account.asset.asset'].browse(rec)
            prec = self.env['decimal.precision'].precision_get('Account')
            company_currency = asset.company_id.currency_id
            current_currency = asset.currency_id
            sub_operating_unit = self.sub_operating_unit_id.id if self.sub_operating_unit_id else None
            cur_sub_operating_unit = asset.sub_operating_unit_id.id if asset.sub_operating_unit_id else False

            if asset.sub_operating_unit_id.id == sub_operating_unit:
                raise ValidationError(_("Same branch transfer shouldn\'t possible."))

            def asset_move(asset):
                last_allocation = self.env['account.asset.allocation.history'].search(
                    [('asset_id', '=', asset.id), ('state', '=', 'active'), ('transfer_date', '=', False)])

                if last_allocation:
                    if last_allocation.receive_date[:10] > self.date:
                        raise ValidationError(
                            _("Asset Allocation/Transfer date shouldn\'t less than previous Allocation/Transfer date."))

                    last_allocation.write({
                        'transfer_date': datetime.strptime(self.date, '%Y-%m-%d') + timedelta(days=-1),
                        'state': 'inactive',
                    })

                return self.env['account.asset.allocation.history'].create({
                    'asset_id': asset.id,
                    'from_branch_id': self.operating_unit_id.id,
                    'operating_unit_id': self.to_operating_unit_id.id,
                    'sub_operating_unit_id': sub_operating_unit,
                    'cost_centre_id': self.cost_centre_id.id,
                    'asset_user': self.asset_user,
                    'receive_date': self.date,
                    'state': 'active',
                })

            if asset.state == 'open' and not asset.depreciation_flag:
                if self.env.context.get('allocation') and not asset.allocation_status:
                    credit = {
                        'name': asset.display_name,
                        'account_id': asset.asset_type_id.asset_suspense_account_id.id,
                        'debit': 0.0,
                        'credit': asset.value if float_compare(asset.value, 0.0, precision_digits=prec) > 0 else 0.0,
                        'journal_id': asset.category_id.journal_id.id,
                        'operating_unit_id': self.operating_unit_id.id,
                        'sub_operating_unit_id': cur_sub_operating_unit,
                        'analytic_account_id': asset.cost_centre_id.id if asset.cost_centre_id else False,
                        'currency_id': company_currency != current_currency and current_currency.id or False,
                    }
                    debit = {
                        'name': asset.display_name,
                        'account_id': asset.asset_type_id.account_asset_id.id,
                        'debit': asset.value if float_compare(asset.value, 0.0, precision_digits=prec) > 0 else 0.0,
                        'credit': 0.0,
                        'journal_id': asset.category_id.journal_id.id,
                        'operating_unit_id': self.to_operating_unit_id.id,
                        'sub_operating_unit_id': sub_operating_unit,
                        'analytic_account_id': self.cost_centre_id.id,
                        'currency_id': company_currency != current_currency and current_currency.id or False,
                    }

                    move = self.env['account.move'].create({
                        'ref': asset.code,
                        'date': self.date or False,
                        'journal_id': asset.category_id.journal_id.id,
                        'operating_unit_id': self.operating_unit_id.id,
                        'sub_operating_unit_id': cur_sub_operating_unit,
                        'line_ids': [(0, 0, debit), (0, 0, credit)],
                    })

                    assetmove = asset_move(asset)
                    assetmove.write({'move_id': move.id})
                    if move.state == 'draft':
                        move.sudo().post()
                    asset.write({'allocation_status': True,
                                 'current_branch_id': self.to_operating_unit_id.id,
                                 'sub_operating_unit_id': sub_operating_unit,
                                 'asset_usage_date': self.date,
                                 'cost_centre_id': self.cost_centre_id.id
                                 })

                elif not self.env.context.get('allocation') and asset.allocation_status:
                    from_total_credit = {
                        'name': asset.display_name,
                        'account_id': asset.category_id.account_asset_id.id,
                        'debit': 0.0,
                        'credit': asset.value if float_compare(asset.value, 0.0, precision_digits=prec) > 0 else 0.0,
                        'journal_id': asset.asset_type_id.journal_id.id,
                        'operating_unit_id': self.operating_unit_id.id,
                        'sub_operating_unit_id': sub_operating_unit,
                        'analytic_account_id': asset.cost_centre_id.id,
                        'currency_id': company_currency != current_currency and current_currency.id or False,
                    }
                    to_total_debit = {
                        'name': asset.display_name,
                        'account_id': asset.asset_type_id.account_asset_id.id,
                        'debit': asset.value if float_compare(asset.value, 0.0, precision_digits=prec) > 0 else 0.0,
                        'credit': 0.0,
                        'journal_id': asset.category_id.journal_id.id,
                        'operating_unit_id': self.to_operating_unit_id.id,
                        'sub_operating_unit_id': sub_operating_unit,
                        'analytic_account_id': self.cost_centre_id.id,
                        'currency_id': company_currency != current_currency and current_currency.id or False,
                    }

                    depr_value = asset.value - asset.value_residual
                    from_depr_credit = {
                        'name': asset.display_name,
                        'account_id': asset.asset_type_id.account_depreciation_id.id,
                        'debit': 0.0,
                        'credit': depr_value if float_compare(depr_value, 0.0, precision_digits=prec) > 0 else 0.0,
                        'journal_id': asset.category_id.journal_id.id,
                        'operating_unit_id': self.to_operating_unit_id.id,
                        'sub_operating_unit_id': sub_operating_unit,
                        'analytic_account_id': self.cost_centre_id.id,
                        'currency_id': company_currency != current_currency and current_currency.id or False,
                    }
                    to_depr_debit = {
                        'name': asset.display_name,
                        'account_id': asset.asset_type_id.account_depreciation_id.id,
                        'debit': depr_value if float_compare(depr_value, 0.0, precision_digits=prec) > 0 else 0.0,
                        'credit': 0.0,
                        'journal_id': asset.category_id.journal_id.id,
                        'operating_unit_id': self.operating_unit_id.id,
                        'sub_operating_unit_id': sub_operating_unit,
                        'analytic_account_id': asset.cost_centre_id.id,
                        'currency_id': company_currency != current_currency and current_currency.id or False,
                    }

                    move = self.env['account.move'].create({
                        'ref': asset.code,
                        'date': self.date or False,
                        'journal_id': asset.category_id.journal_id.id,
                        'operating_unit_id': self.operating_unit_id.id,
                        'sub_operating_unit_id': cur_sub_operating_unit,
                        'line_ids': [(0, 0, from_total_credit), (0, 0, to_total_debit),
                                     (0, 0, from_depr_credit), (0, 0, to_depr_debit)],
                    })

                    assetmove = asset_move(asset)
                    assetmove.write({'move_id': move.id})
                    if move.state == 'draft':
                        move.sudo().post()
                    asset.write({'current_branch_id': self.to_operating_unit_id.id,
                                 'sub_operating_unit_id': sub_operating_unit,
                                 'cost_centre_id': self.cost_centre_id.id
                                 })
            else:
                flag = 'Active' if asset.depreciation_flag else 'In-Active'
                raise Warning(_('Asset [{0}] is in Status [{1}] with Awaiting Disposal [{2}]'.format(asset.display_name,
                                                                                                     asset.state,
                                                                                                     flag)))
        return {'type': 'ir.actions.act_window_close'}
