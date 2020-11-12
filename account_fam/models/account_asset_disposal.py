# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.tools import float_compare, float_is_zero

DATE_FORMAT = "%Y-%m-%d"


class AccountAssetDisposal(models.Model):
    _name = 'account.asset.disposal'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'name desc,id desc'
    _rec_name = 'name'
    _description = "Asset Written-Off"

    name = fields.Char(string='Serial No', readonly=True, default='New', track_visibility='onchange')
    total_value = fields.Float(string='Cost Value', compute='_compute_total_value', track_visibility='onchange')
    total_depr_amount = fields.Float(string='Total Accumulated Depr.', compute='_compute_total_depr_amount',
                                     track_visibility='onchange')
    narration = fields.Char(string="Narration", required=True, readonly=True, size=50,
                            states={'draft': [('readonly', False)]}, track_visibility='onchange')
    narration_gl = fields.Char(string="Narration Gain/Loss", required=True, readonly=True, size=50,
                               states={'draft': [('readonly', False)]}, track_visibility='onchange')
    request_date = fields.Date(string='Request Date', required=True,
                               default=lambda self: self.env.user.company_id.batch_date,
                               readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    approve_date = fields.Date(string='Approve Date', readonly=True, states={'draft': [('readonly', False)]},
                               track_visibility='onchange')
    dispose_date = fields.Date(string='Dispose Date', readonly=True, states={'approve': [('readonly', False)]},
                               track_visibility='onchange')
    request_user_id = fields.Many2one('res.users', string='Request', readonly=True,
                                      states={'draft': [('readonly', False)]}, default=lambda self: self.env.user,
                                      track_visibility='onchange')
    approve_user_id = fields.Many2one('res.users', string='Maker', readonly=True,
                                      states={'draft': [('readonly', False)]}, track_visibility='onchange')
    dispose_user_id = fields.Many2one('res.users', string='Checker', readonly=True,
                                      states={'approve': [('readonly', False)]}, track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    branch_id = fields.Many2one('operating.unit', string='Branch', required=True, readonly=True,
                                states={'draft': [('readonly', False)]})
    note = fields.Text(string='Note', readonly=True, states={'draft': [('readonly', False)]},
                       track_visibility='onchange')
    line_ids = fields.One2many('account.asset.disposal.line', 'dispose_id', string='Disposal Line', readonly=True,
                               states={'draft': [('readonly', False)]}, track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('dispose', 'Confirmed')], default='draft',
                             string='State', track_visibility='onchange')

    @api.depends('line_ids')
    def _compute_total_value(self):
        for rec in self:
            rec.total_value = sum(rec.cost_value for rec in rec.line_ids)

    @api.onchange('branch_id')
    def _onchange_branch(self):
        if self.branch_id:
            self.line_ids = []

    @api.depends('line_ids')
    def _compute_total_depr_amount(self):
        for rec in self:
            rec.total_depr_amount = sum(rec.depreciation_value for rec in rec.line_ids)

    @api.one
    def action_approve(self):
        if len(self.line_ids) <= 0:
            raise ValidationError(_('[Warning] Dispose List should not be empty.'))

        if self.state == 'draft':
            single, duplicate, sell = [], [], []
            dup_str, sell_str = '', ''
            for val in self.line_ids:
                if val.asset_id.asset_status != 'active':
                    sell.append(val.asset_id.asset_seq)
                    sell_str = sell_str + "- {0}\t\n".format(val.asset_id.asset_seq)
                if val.asset_id.asset_seq not in single:
                    single.append(val.asset_id.asset_seq)
                else:
                    dup_str = dup_str + "- {0}\t\n".format(val.asset_id.asset_seq)
                    duplicate.append(val.asset_id.asset_seq)

            if len(sell) > 0:
                raise ValidationError(_(
                    "[PROCESSED] Following assets are already Sold or Dispose.\n\n{0}".format(sell_str)))
            elif len(duplicate) > 0:
                raise ValidationError(_(
                    "[DUPLICATE] Following assets are duplicate in line.\n\n{0}".format(dup_str)))

            for rec in self.line_ids:
                rec.asset_id.write({'asset_status': 'dispose'})

        if self.state == 'draft':
            self.write({
                'name': self.env['ir.sequence'].next_by_code('account.asset.disposal') or _('New'),
                'state': 'approve',
                'approve_date': self.env.user.company_id.batch_date,
                'approve_user_id': self.env.user.id,
            })

    @api.one
    def action_dispose(self):
        if self.state == 'approve':
            if self.env.user.id == self.approve_user_id.id and self.env.user.id != SUPERUSER_ID:
                raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))

            for rec in self.line_ids:
                date = datetime.strptime(self.env.user.company_id.batch_date, DATE_FORMAT)
                dispose = self.generate_move(rec.asset_id)
                if dispose.state == 'draft':
                    dispose.post()
                    rec.write({'journal_entry': 'post', 'move_id': dispose.id})
                    response = rec.asset_id.set_to_close(date)

            self.write({
                'state': 'dispose',
                'dispose_date': self.env.user.company_id.batch_date,
                'dispose_user_id': self.env.user.id,
            })

    def generate_move(self, asset):
        prec = self.env['decimal.precision'].precision_get('Account')
        company_currency = asset.company_id.currency_id
        current_currency = asset.currency_id

        credit = {
            'name': self.narration,
            'account_id': asset.asset_type_id.account_asset_id.id,
            'credit': round(asset.value, 2) if float_compare(asset.value, 0.0, precision_digits=prec) > 0 else 0.0,
            'debit': 0.0,
            'journal_id': asset.asset_type_id.journal_id.id,
            'operating_unit_id': asset.current_branch_id.id,
            'sub_operating_unit_id': asset.asset_type_id.account_asset_seq_id.id if asset.asset_type_id else None,
            'analytic_account_id': asset.cost_centre_id.id if asset.cost_centre_id else None,
            'currency_id': company_currency != current_currency and current_currency.id or False,
        }

        debit = {
            'name': self.narration,
            'account_id': asset.asset_type_id.account_depreciation_id.id,
            'credit': 0.0,
            'debit': round(asset.accumulated_value, 2) if float_compare(asset.accumulated_value, 0.0,
                                                                        precision_digits=prec) > 0 else 0.0,
            'journal_id': asset.asset_type_id.journal_id.id,
            'operating_unit_id': asset.current_branch_id.id,
            'sub_operating_unit_id': asset.asset_type_id.account_depreciation_seq_id.id if asset.asset_type_id else None,
            'analytic_account_id': asset.cost_centre_id.id if asset.cost_centre_id else None,
            'currency_id': company_currency != current_currency and current_currency.id or False,
        }

        debit2 = {
            'name': self.narration_gl,
            'account_id': asset.asset_type_id.account_asset_loss_id.id,
            'credit': 0.0,
            'debit': round(asset.value_residual, 2) if float_compare(asset.value_residual, 0.0,
                                                                     precision_digits=prec) > 0 else 0.0,
            'journal_id': asset.asset_type_id.journal_id.id,
            'operating_unit_id': asset.current_branch_id.id,
            'sub_operating_unit_id': asset.asset_type_id.account_asset_loss_seq_id.id if asset.asset_type_id else None,
            'analytic_account_id': asset.cost_centre_id.id if asset.cost_centre_id else None,
            'currency_id': company_currency != current_currency and current_currency.id or False,
        }

        # if credit >0 and debit>
        return self.env['account.move'].create({
            'ref': asset.code,
            'date': self.env.user.company_id.batch_date,
            'journal_id': asset.category_id.journal_id.id,
            'operating_unit_id': asset.current_branch_id.id,
            'sub_operating_unit_id': asset.sub_operating_unit_id.id,
            'maker_id': self.approve_user_id.id,
            'approver_id': self.env.user.id,
            'line_ids': [(0, 0, credit), (0, 0, debit), (0, 0, debit2)],
        })

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'dispose'):
                raise ValidationError(_('[Warning] Approved and Disposed Record cannot deleted.'))
        return super(AccountAssetDisposal, self).unlink()

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'approve')]


class AccountAssetDisposalLine(models.Model):
    _name = 'account.asset.disposal.line'
    _rec = 'id ASC'

    asset_id = fields.Many2one('account.asset.asset', required=True, string='Asset Name')
    cost_value = fields.Float(related='asset_id.value', string='Cost Value', required=True, digits=(14, 2))
    asset_value = fields.Float(string='WDV', required=True, digits=(14, 2))
    depreciation_value = fields.Float(string='Accumulated Depr.', required=True, digits=(14, 2))

    dispose_id = fields.Many2one('account.asset.disposal', string='Disposal', ondelete='restrict')
    journal_entry = fields.Selection([('unpost', 'Unposted'), ('post', 'Posted')], default='unpost', requried=True)
    move_id = fields.Many2one('account.move', string='Journal')

    @api.onchange('asset_id')
    def onchange_asset(self):
        if self.asset_id:
            depreciated_value = sum([val.amount for val in self.asset_id.depreciation_line_ids])
            self.depreciation_value = depreciated_value
            self.asset_value = self.asset_id.value - depreciated_value
