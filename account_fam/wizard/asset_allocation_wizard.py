# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
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

    asset_user = fields.Char("Asset User")
    date = fields.Date(string='Allocation/Transfer Date', required=True, default=fields.Date.today())
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
        asset_id = self.env.context.get('active_id', False)
        asset = self.env['account.asset.asset'].browse(asset_id)
        prec = self.env['decimal.precision'].precision_get('Account')
        company_currency = asset.company_id.currency_id
        current_currency = asset.currency_id

        if self.operating_unit_id.id == self.to_operating_unit_id.id:
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
                'sub_operating_unit_id': self.sub_operating_unit_id.id,
                'cost_centre_id': self.cost_centre_id.id,
                'asset_user': self.asset_user,
                'receive_date': self.date,
                'state': 'active',
            })

        if self.env.context.get('allocation'):
            credit = {
                'name': asset.display_name,
                'account_id': asset.category_id.asset_suspense_account_id.id,
                'debit': 0.0,
                'credit': asset.value if float_compare(asset.value, 0.0, precision_digits=prec) > 0 else 0.0,
                'journal_id': asset.category_id.journal_id.id,
                'partner_id': asset.partner_id.id,
                'operating_unit_id': self.operating_unit_id.id,
                'currency_id': company_currency != current_currency and current_currency.id or False,
            }
            debit = {
                'name': asset.display_name,
                'account_id': asset.category_id.account_asset_id.id,
                'debit': asset.value if float_compare(asset.value, 0.0, precision_digits=prec) > 0 else 0.0,
                'credit': 0.0,
                'journal_id': asset.category_id.journal_id.id,
                'partner_id': asset.partner_id.id,
                'operating_unit_id': self.to_operating_unit_id.id,
                'currency_id': company_currency != current_currency and current_currency.id or False,
            }

            move = self.env['account.move'].create({
                'ref': asset.code,
                'date': self.date or False,
                'journal_id': asset.category_id.journal_id.id,
                'operating_unit_id': self.to_operating_unit_id.id,
                'line_ids': [(0, 0, debit), (0, 0, credit)],
            })

            assetmove = asset_move(asset)
            assetmove.write({'move_id': move.id})
            move.post()
            asset.write({'allocation_status': True, 'current_branch_id': self.to_operating_unit_id.id,
                         'asset_usage_date': self.date})

        if self.env.context.get('transfer'):
            from_total_credit = {
                'name': asset.display_name,
                'account_id': asset.category_id.account_asset_id.id,
                'debit': 0.0,
                'credit': asset.value if float_compare(asset.value, 0.0, precision_digits=prec) > 0 else 0.0,
                'journal_id': asset.category_id.journal_id.id,
                'partner_id': asset.partner_id.id,
                'operating_unit_id': self.operating_unit_id.id,
                'currency_id': company_currency != current_currency and current_currency.id or False,
            }
            to_total_debit = {
                'name': asset.display_name,
                'account_id': asset.category_id.account_asset_id.id,
                'debit': asset.value if float_compare(asset.value, 0.0, precision_digits=prec) > 0 else 0.0,
                'credit': 0.0,
                'journal_id': asset.category_id.journal_id.id,
                'partner_id': asset.partner_id.id,
                'operating_unit_id': self.to_operating_unit_id.id,
                'currency_id': company_currency != current_currency and current_currency.id or False,
            }

            depr_value = asset.value - asset.value_residual
            from_depr_credit = {
                'name': asset.display_name,
                'account_id': asset.category_id.account_depreciation_id.id,
                'debit': 0.0,
                'credit': depr_value if float_compare(depr_value, 0.0, precision_digits=prec) > 0 else 0.0,
                'journal_id': asset.category_id.journal_id.id,
                'partner_id': asset.partner_id.id,
                'operating_unit_id': self.to_operating_unit_id.id,
                'currency_id': company_currency != current_currency and current_currency.id or False,
            }
            to_depr_debit = {
                'name': asset.display_name,
                'account_id': asset.category_id.account_depreciation_id.id,
                'debit': depr_value if float_compare(depr_value, 0.0, precision_digits=prec) > 0 else 0.0,
                'credit': 0.0,
                'journal_id': asset.category_id.journal_id.id,
                'partner_id': asset.partner_id.id,
                'operating_unit_id': self.operating_unit_id.id,
                'currency_id': company_currency != current_currency and current_currency.id or False,
            }

            move = self.env['account.move'].create({
                'ref': asset.code,
                'date': self.date or False,
                'journal_id': asset.category_id.journal_id.id,
                'operating_unit_id': self.to_operating_unit_id.id,
                'line_ids': [(0, 0, from_total_credit), (0, 0, to_total_debit),
                             (0, 0, from_depr_credit), (0, 0, to_depr_debit)],
            })

            assetmove = asset_move(asset)
            assetmove.write({'move_id': move.id})
            move.post()
            asset.write({'current_branch_id': self.to_operating_unit_id.id})

        return {'type': 'ir.actions.act_window_close'}
