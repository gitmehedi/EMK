# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning
from odoo.tools import float_compare, float_is_zero

DATE_FORMAT = "%Y-%m-%d"


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
            return self.env.user.company_id.batch_date

    def default_warranty_date(self):
        return self.env.user.company_id.batch_date

    def default_status(self):
        if 'allocation' in self.env.context:
            return self.env.context['allocation']
        else:
            return False

    asset_user = fields.Char("Asset User")
    date = fields.Date(string='Allocation/Transfer Date', required=True, default=default_date)
    warranty_date = fields.Date(string='Warranty Date', default=default_warranty_date)
    usage_date = fields.Date(string='Usage Date', default=default_warranty_date)
    operating_unit_id = fields.Many2one('operating.unit', string='From Branch', readonly=True,
                                        default=default_from_branch)
    to_operating_unit_id = fields.Many2one('operating.unit', string='To Branch', required=True)
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='To Sequence')
    cost_centre_id = fields.Many2one('account.analytic.account', string='To Cost Centre', required=True)
    narration = fields.Char(string='Narration', required=True)
    is_allocate = fields.Boolean(default=default_status)

    @api.constrains('date', 'warranty_date', 'usage_date')
    def check_warranty_date(self):
        sys_date = self.env.user.company_id.batch_date

        if self.usage_date:
            provision_diff = datetime.strptime(sys_date, DATE_FORMAT) - relativedelta(years=3)
            provision_date = provision_diff.strftime(DATE_FORMAT)

            if self.usage_date > sys_date:
                raise ValidationError(
                    _('Usage date [{0}] should not be greater than current OGL application date [{1}]'.format(
                        self.usage_date, sys_date)))
            if provision_date > self.usage_date:
                raise ValidationError(
                    _(
                        'Usage date [{0}] should not be less than 3 years earlier from OGL application date [{1}].'.format(
                            self.usage_date, sys_date)))
        if self.warranty_date:
            if self.usage_date > self.warranty_date:
                raise ValidationError(_('Warranty date [{0}] should not be less than usage date [{1}].'.format(
                    self.warranty_date, self.usage_date)))

    @api.multi
    def allocation(self):
        for rec in self._context['active_ids']:
            asset = self.env['account.asset.asset'].browse(rec)
            prec = self.env['decimal.precision'].precision_get('Account')
            company_currency = asset.company_id.currency_id
            current_currency = asset.currency_id
            to_sub_operating_unit = self.sub_operating_unit_id.id
            cur_sub_operating_unit = asset.sub_operating_unit_id.id

            if asset.sub_operating_unit_id.id == to_sub_operating_unit:
                raise ValidationError(_("Same branch transfer shouldn\'t possible."))

            def asset_move(asset):
                last_allocation = self.env['account.asset.allocation.history'].search(
                    [('asset_id', '=', asset.id), ('state', '=', 'active'), ('transfer_date', '=', False)])

                if last_allocation:
                    if last_allocation.receive_date[:10] > self.date:
                        raise ValidationError(
                            _("Asset Allocation/Transfer date shouldn\'t less than previous Allocation/Transfer date."))

                    last_allocation.write({
                        'transfer_date': datetime.strptime(self.date, '%Y-%m-%d'),
                        'state': 'inactive',
                    })

                return self.env['account.asset.allocation.history'].create({
                    'asset_id': asset.id,
                    'from_branch_id': self.operating_unit_id.id,
                    'operating_unit_id': self.to_operating_unit_id.id,
                    # 'sub_operating_unit_id': to_sub_operating_unit,
                    'cost_centre_id': self.cost_centre_id.id,
                    'asset_user': self.asset_user,
                    'receive_date': self.date,
                    'state': 'active',
                })

            if asset.state == 'open' and not asset.depreciation_flag:
                if self.env.context.get('allocation') and not asset.allocation_status:
                    credit = {
                        'name': self.narration,
                        'account_id': asset.asset_type_id.asset_suspense_account_id.id,
                        'debit': 0.0,
                        'credit': asset.value if float_compare(asset.value, 0.0, precision_digits=prec) > 0 else 0.0,
                        'journal_id': asset.asset_type_id.journal_id.id,
                        'operating_unit_id': asset.current_branch_id.id,
                        'sub_operating_unit_id': asset.asset_type_id.asset_suspense_seq_id.id,
                        'analytic_account_id': asset.cost_centre_id.id if asset.cost_centre_id else False,
                        'currency_id': company_currency != current_currency and current_currency.id or False,
                        'reconcile_ref': asset.reconcile_ref if asset.asset_type_id.asset_suspense_account_id.reconcile else '',
                    }
                    debit = {
                        'name': self.narration,
                        'account_id': asset.asset_type_id.account_asset_id.id,
                        'debit': asset.value if float_compare(asset.value, 0.0, precision_digits=prec) > 0 else 0.0,
                        'credit': 0.0,
                        'journal_id': asset.asset_type_id.journal_id.id,
                        'operating_unit_id': self.to_operating_unit_id.id,
                        'sub_operating_unit_id': asset.asset_type_id.account_asset_seq_id.id,
                        'analytic_account_id': self.cost_centre_id.id,
                        'currency_id': company_currency != current_currency and current_currency.id or False,
                        'reconcile_ref': asset.reconcile_ref if asset.asset_type_id.account_asset_id.reconcile else '',
                    }

                    move = self.env['account.move'].create({
                        'ref': 'Asset Allocation Branch [{0}] to [{1}]'.format(self.operating_unit_id.name,
                                                                               self.to_operating_unit_id.name),
                        'journal_id': asset.asset_type_id.journal_id.id,
                        'operating_unit_id': self.operating_unit_id.id,
                        'maker_id': self.env.user.id,
                        'approver_id': self.env.user.id,
                        'line_ids': [(0, 0, debit), (0, 0, credit)],
                    })

                    assetmove = asset_move(asset)
                    assetmove.write({'move_id': move.id})
                    if move.state == 'draft':
                        move.sudo().post()
                    asset.write({'allocation_status': True,
                                 'current_branch_id': self.to_operating_unit_id.id,
                                 # 'sub_operating_unit_id': to_sub_operating_unit,
                                 'asset_usage_date': self.usage_date,
                                 'cost_centre_id': self.cost_centre_id.id,
                                 'warranty_date': self.warranty_date
                                 })

                    if not asset.asset_seq and asset.date and asset.asset_type_id.code:
                        date = self.date.split('-')
                        count = asset.asset_type_id.asset_count + 1
                        code = '{0}-{1}-MTB-{2}-{3}'.format(date[0],
                                                            date[1].zfill(2),
                                                            asset.asset_type_id.code,
                                                            str(count).zfill(5))
                        asset.write({'asset_seq': code})
                        asset.asset_type_id.write({'asset_count': count})
                    else:
                        raise ValidationError(_('Purchase Date or Asset Category is not available.'))
                elif not self.env.context.get('allocation') and asset.allocation_status:
                    from_total_credit = {
                        'name': self.narration,
                        'account_id': asset.asset_type_id.account_asset_id.id,
                        'debit': 0.0,
                        'credit': asset.value if float_compare(asset.value, 0.0, precision_digits=prec) > 0 else 0.0,
                        'journal_id': asset.asset_type_id.journal_id.id,
                        'operating_unit_id': self.operating_unit_id.id,
                        'sub_operating_unit_id': asset.asset_type_id.account_asset_seq_id.id,
                        'analytic_account_id': asset.cost_centre_id.id,
                        'currency_id': company_currency != current_currency and current_currency.id or False,
                        'reconcile_ref': asset.reconcile_ref if asset.asset_type_id.account_asset_id.reconcile else '',
                    }
                    to_total_debit = {
                        'name': self.narration,
                        'account_id': asset.asset_type_id.account_asset_id.id,
                        'debit': asset.value if float_compare(asset.value, 0.0, precision_digits=prec) > 0 else 0.0,
                        'credit': 0.0,
                        'journal_id': asset.asset_type_id.journal_id.id,
                        'operating_unit_id': self.to_operating_unit_id.id,
                        'sub_operating_unit_id': asset.asset_type_id.account_asset_seq_id.id,
                        'analytic_account_id': self.cost_centre_id.id,
                        'currency_id': company_currency != current_currency and current_currency.id or False,
                        'reconcile_ref': asset.reconcile_ref if asset.asset_type_id.account_asset_id.reconcile else '',
                    }

                    depr_value = asset.value - asset.value_residual
                    from_depr_credit = {
                        'name': self.narration,
                        'account_id': asset.asset_type_id.account_depreciation_id.id,
                        'debit': 0.0,
                        'credit': depr_value if float_compare(depr_value, 0.0, precision_digits=prec) > 0 else 0.0,
                        'journal_id': asset.asset_type_id.journal_id.id,
                        'operating_unit_id': self.to_operating_unit_id.id,
                        'sub_operating_unit_id': asset.asset_type_id.account_depreciation_seq_id.id,
                        'analytic_account_id': self.cost_centre_id.id,
                        'currency_id': company_currency != current_currency and current_currency.id or False,
                        'reconcile_ref': asset.reconcile_ref if asset.asset_type_id.account_depreciation_id.reconcile else '',
                    }
                    to_depr_debit = {
                        'name': self.narration,
                        'account_id': asset.asset_type_id.account_depreciation_id.id,
                        'debit': depr_value if float_compare(depr_value, 0.0, precision_digits=prec) > 0 else 0.0,
                        'credit': 0.0,
                        'journal_id': asset.asset_type_id.journal_id.id,
                        'operating_unit_id': self.operating_unit_id.id,
                        'sub_operating_unit_id': asset.asset_type_id.account_depreciation_seq_id.id,
                        'analytic_account_id': asset.cost_centre_id.id,
                        'currency_id': company_currency != current_currency and current_currency.id or False,
                        'reconcile_ref': asset.reconcile_ref if asset.asset_type_id.account_depreciation_id.reconcile else '',
                    }

                    move = self.env['account.move'].create({
                        'ref': 'Asset Transfer Branch [{0}] to [{1}]'.format(self.operating_unit_id.name,
                                                                             self.to_operating_unit_id.name),
                        'journal_id': asset.asset_type_id.journal_id.id,
                        'operating_unit_id': self.operating_unit_id.id,
                        'maker_id': self.env.user.id,
                        'approver_id': self.env.user.id,
                        'line_ids': [(0, 0, from_total_credit), (0, 0, to_total_debit),
                                     (0, 0, from_depr_credit), (0, 0, to_depr_debit)],
                    })

                    assetmove = asset_move(asset)
                    assetmove.write({'move_id': move.id})
                    if move.state == 'draft':
                        move.sudo().post()
                    asset.write({'current_branch_id': self.to_operating_unit_id.id,
                                 'cost_centre_id': self.cost_centre_id.id
                                 })
            else:
                flag = 'Active' if asset.depreciation_flag else 'In-Active'
                raise ValidationError(
                    _('Asset [{0}] is in Status [{1}] with Awaiting Disposal [{2}]'.format(asset.display_name,
                                                                                           asset.state,
                                                                                           flag)))
        return {'type': 'ir.actions.act_window_close'}
