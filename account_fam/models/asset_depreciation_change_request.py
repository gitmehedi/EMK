from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import Warning, ValidationError
from odoo.tools import float_compare, float_is_zero

DATE_FORMAT = "%Y-%m-%d"


class AssetDepreciationChangeRequest(models.Model):
    _name = 'asset.depreciation.change.request'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Asset Depreciation Method Change'
    _order = 'id desc'
    _depreciation = []

    name = fields.Char(required=False, track_visibility='onchange', string='Name')
    asset_life = fields.Integer('Asset Life (In Year)', required=True, readonly=True,
                                states={'draft': [('readonly', False)]})
    narration = fields.Char('Narration', readonly=True, size=30,required=True, states={'draft': [('readonly', False)]})
    method_progress_factor = fields.Float('Depreciation Factor', readonly=True, states={'draft': [('readonly', False)]})
    change_date = fields.Date('Change Date', readonly=True, states={'draft': [('readonly', False)]})
    request_date = fields.Date('Requested Date', default=fields.Date.today, readonly=True,
                               states={'draft': [('readonly', False)]})
    approve_date = fields.Date('Approved Date', readonly=True, states={'draft': [('readonly', False)]})
    asset_cat_id = fields.Many2one('account.asset.category', track_visibility='onchange', required=True,
                                   domain=[('parent_id', '!=', False), ('method', '=', 'degressive')],
                                   string='Asset Category', readonly=True,
                                   states={'draft': [('readonly', False)]})
    method = fields.Selection([('linear', 'Straight Line/Linear')], default='linear', string="Computation Method",
                              track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user.id, track_visibility='onchange')
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange')
    move_id = fields.Many2one('account.move', string='Journal', track_visibility='onchange', readonly=True)
    line_ids = fields.One2many('asset.depreciation.change.request.line', 'line_id', track_visibility='onchange',
                               readonly=True, states={'draft': [('readonly', False)]})

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

    @api.constrains('asset_cat_id', 'method')
    def check_asset_cat_id(self):
        if self.asset_cat_id.method == self.method:
            raise Warning(_('Asset Category current method and change request method should not be same.'))

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
                history = self.env['history.account.asset.category'].create({'method': self.method,
                                                                             'depreciation_year': self.asset_life,
                                                                             'method_progress_factor': 0.0,
                                                                             'request_date': fields.Datetime.now(),
                                                                             'line_id': category.id,
                                                                             })
                category.write({'pending': True})
                category.act_approve_pending()

            assets = self.env['account.asset.asset'].search([('asset_type_id', '=', self.asset_cat_id.id)])
            move = None
            lines = []

            for asset in assets:
                dmc_date = datetime.strptime(asset.date, DATE_FORMAT) + relativedelta(years=self.asset_life)
                system_date = datetime.strptime(self.env.user.company_id.batch_date, DATE_FORMAT)
                if system_date > dmc_date:
                    if not move:
                        move = self.env['account.move'].create({
                            'ref': self.narration,
                            'date': system_date,
                            'journal_id': asset.category_id.journal_id.id,
                            'operating_unit_id': asset.current_branch_id.id
                        })
                    vals = self.modify(move, asset, dmc_date)
                    if vals:
                        lines.append((0, 0, vals[0]))
                        lines.append((0, 0, vals[1]))

                    # self.line_ids.create({'asset_id': asset.id, 'line_id': self.id})

            if move:
                if len(lines) > 1:
                    move.write({'line_ids': lines})
                    if move.state == 'draft':
                        move.sudo().post()
                else:
                    move.unlink()

            self.write({
                'state': 'approve',
                'approver_id': self.env.user.id,
                'move_id': move.id or False,
                'approve_date': fields.Date.today()
            })

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'confirm')]

    @api.multi
    def modify(self, move, asset, dmc_date):
        if asset.state == 'open' and not asset.depreciation_flag:
            if asset.value_residual > 0 and asset.allocation_status == True:
                depr_value = asset.value_residual
                depreciated_amount = asset.accumulated_value + depr_value
                remaining_value = asset.value - depreciated_amount
                vals = {
                    'amount': depr_value,
                    'asset_id': asset.id,
                    'sequence': 1,
                    'name': asset.code or '/',
                    'remaining_value': abs(remaining_value),
                    'depreciated_value': depreciated_amount,
                    'depreciation_date': self.env.user.company_id.batch_date,
                    'days': 0,
                    'asset_id': asset.id,
                    'move_id': move.id,
                    'move_check': True,
                }

                line = asset.depreciation_line_ids.create(vals)

                if line:
                    record = self.create_depr(move, asset, depr_value)
                    asset.write({'method': self.method,
                                 'depreciation_year': self.asset_life,
                                 'method_progress_factor': 0.0,
                                 'dmc_date': dmc_date,
                                 'lst_depr_date': self.env.user.company_id.batch_date,
                                 'lst_depr_amount': depreciated_amount,
                                 'state': 'open',
                                 })
                    return record

    def create_depr(self, move, asset, depr_value):
        prec = self.env['decimal.precision'].precision_get('Account')
        company_currency = asset.company_id.currency_id
        current_currency = asset.currency_id
        category = asset.asset_type_id
        credit = {
            'name': self.narration,
            'debit': 0.0,
            'credit': depr_value if float_compare(depr_value, 0.0, precision_digits=prec) > 0 else 0.0,
            'journal_id': category.journal_id.id,
            'operating_unit_id': asset.current_branch_id.id,
            'account_id': category.account_depreciation_id.id,
            'sub_operating_unit_id': category.account_depreciation_seq_id.id,
            'analytic_account_id': asset.cost_centre_id.id if asset.cost_centre_id else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'move_id': move.id
        }
        debit = {
            'name': self.narration,
            'debit': depr_value if float_compare(depr_value, 0.0, precision_digits=prec) > 0 else 0.0,
            'credit': 0.0,
            'journal_id': asset.category_id.journal_id.id,
            'operating_unit_id': asset.current_branch_id.id,
            'account_id': category.account_depreciation_expense_id.id,
            'sub_operating_unit_id': category.account_depreciation_expense_seq_id.id,
            'analytic_account_id': asset.cost_centre_id.id,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'move_id': move.id
        }
        return debit, credit


class AssetDepreciationChangeRequestLine(models.Model):
    _name = 'asset.depreciation.change.request.line'

    asset_id = fields.Many2one('account.asset.asset', string='Asset Name', required=True)
    line_id = fields.Many2one('asset.depreciation.change.request')
