from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import Warning, ValidationError

DATE_FORMAT = "%Y-%m-%d"


class AssetDepreciationChangeRequest(models.Model):
    _name = 'asset.depreciation.change.request'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Asset Depreciation Change Request'
    _order = 'name desc'

    name = fields.Char(required=False, track_visibility='onchange', string='Name')
    asset_life = fields.Integer('Asset Life (In Year)', required=True, readonly=True,
                                states={'draft': [('readonly', False)]})
    narration = fields.Text('Narration', readonly=True, states={'draft': [('readonly', False)]})
    method_progress_factor = fields.Float('Depreciation Factor', readonly=True, states={'draft': [('readonly', False)]})
    change_date = fields.Date('Change Date', readonly=True, states={'draft': [('readonly', False)]})
    request_date = fields.Date('Requested Date', default=fields.Date.today, readonly=True,
                               states={'draft': [('readonly', False)]})
    approve_date = fields.Date('Approved Date', readonly=True, states={'draft': [('readonly', False)]})
    asset_cat_id = fields.Many2one('account.asset.category', track_visibility='onchange', required=True,
                                   domain=[('parent_id', '!=', False)], string='Asset Category', readonly=True,
                                   states={'draft': [('readonly', False)]})
    method = fields.Selection([('linear', 'Straight Line/Linear')], default='linear', string="Computation Method",
                              track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user.id, track_visibility='onchange')
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange')

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirmed"),
        ('approve', "Approved"),
        ('cancel', "Canceled")], default='draft', string="Status",
        track_visibility='onchange')

    @api.constrains('asset_life')
    def check_asset_life(self):
        if self.asset_life < 1:
            raise Warning(_('Asset life should be a valid value.'))

    @api.one
    def action_confirm(self):
        if self.state == 'draft':
            if not self.name:
                name = self.env['ir.sequence'].sudo().next_by_code('asset.depreciation.change.request')
                name = name.replace('CAT', self.asset_cat_id.code)
            self.write({
                'state': 'confirm',
                'name': name,
                'maker_id': self.env.user.id,
            })

    @api.one
    def action_approve(self):
        if self.state == 'confirm':
            if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
                raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))

            category = self.env['account.asset.category'].search([('id', '=', self.asset_cat_id.id)])
            if category:
                history = self.env['history.account.asset.category'].create(
                    {'method': self.method,
                     'depreciation_year': self.asset_life,
                     'method_progress_factor': 0.0,
                     'request_date': fields.Datetime.now(),
                     })
                category.write({'pending': True})
                category.act_approve_pending()

            assets = self.env['account.asset.asset'].search([('asset_type_id', '=', self.asset_cat_id.id)])

            for asset in assets:
                dmc_date = datetime.strptime(asset.date, DATE_FORMAT) + relativedelta(years=self.asset_life)
                if datetime.now() > dmc_date:
                    value_residual = asset.value_residual
                    vals = self.modify(asset)

                    asset.write({'method': self.method,
                                 'depreciation_year': self.asset_life,
                                 'method_progress_factor': 0.0,
                                 'dmc_date': dmc_date,
                                 })

                # else:
                #     print('--------------', asset.id)
                #     asset.write({'method': self.method,
                #                  'depreciation_year': self.asset_life,
                #                  'method_progress_factor': 0.0,
                #                  'dmc_date': dmc_date,
                #                  })

            self.write({
                'state': 'approve',
                'approver_id': self.env.user.id,
                'approve_date': fields.Date.today()
            })

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'confirm')]

    @api.multi
    def modify(self, asset, dmc_date):
        if asset.state == 'open' and not asset.depreciation_flag:
            old_values = {
                'method': asset.method,
                'depreciation_year': asset.depreciation_year,
                'method_progress_factor': asset.method_progress_factor,
                'dmc_date': dmc_date,
            }
            asset_vals = {
                'method': self.method,
                'depreciation_year': self.depreciation_year,
                'method_progress_factor': self.method_progress_factor,
                'dmc_date': dmc_date,
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
        # else:
        #     flag = 'Active' if asset.depreciation_flag else 'In-Active'
        #     raise Warning(_('Depreciation of Asset {0} is in Status [{1}] with Awaiting Disposal [{2}]'.format(
        #         asset.display_name,asset.state, flag)))

        # return {'type': 'ir.actions.act_window_close'}

    def create_move(self, asset, depr_value):
        prec = self.env['decimal.precision'].precision_get('Account')
        # company_currency = asset.company_id.currency_id
        # current_currency = asset.currency_id
        # sub_operating_unit = asset.sub_operating_unit_id.id if asset.sub_operating_unit_id else None
        # credit = {
        #     'name': asset.display_name,
        #     'account_id': asset.asset_type_id.account_depreciation_id.id,
        #     'debit': 0.0,
        #     'credit': depr_value if float_compare(depr_value, 0.0,
        #                                           precision_digits=prec) > 0 else 0.0,
        #     'journal_id': asset.category_id.journal_id.id,
        #     'operating_unit_id': asset.current_branch_id.id,
        #     'sub_operating_unit_id': sub_operating_unit,
        #     'analytic_account_id': asset.cost_centre_id.id if asset.cost_centre_id else False,
        #     'currency_id': company_currency != current_currency and current_currency.id or False,
        # }
        # debit = {
        #     'name': asset.display_name,
        #     'account_id': asset.asset_type_id.account_depreciation_expense_id.id,
        #     'debit': depr_value if float_compare(depr_value, 0.0,
        #                                          precision_digits=prec) > 0 else 0.0,
        #     'credit': 0.0,
        #     'journal_id': asset.category_id.journal_id.id,
        #     'operating_unit_id': asset.current_branch_id.id,
        #     'sub_operating_unit_id': sub_operating_unit,
        #     'analytic_account_id': asset.cost_centre_id.id,
        #     'currency_id': company_currency != current_currency and current_currency.id or False,
        # }
        #
        # return self.env['account.move'].create({
        #     'ref': asset.code,
        #     'date': fields.Datetime.now() or False,
        #     'journal_id': asset.category_id.journal_id.id,
        #     'operating_unit_id': asset.current_branch_id.id,
        #     'sub_operating_unit_id': sub_operating_unit,
        #     'line_ids': [(0, 0, debit), (0, 0, credit)],
        # })
