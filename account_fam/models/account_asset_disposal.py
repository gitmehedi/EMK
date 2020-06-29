# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning
from datetime import datetime
from odoo.tools import float_compare, float_is_zero

DATE_FORMAT = "%Y-%m-%d"


class AccountAssetDisposal(models.Model):
    _name = 'account.asset.disposal'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'name desc,id desc'
    _rec_name = 'name'

    name = fields.Char(string='Serial No', readonly=True, default='New', track_visibility='onchange')
    total_value = fields.Float(string='Cost Value', compute='_compute_total_value', track_visibility='onchange')
    total_depr_amount = fields.Float(string='Total Accumulated Depr.', compute='_compute_total_depr_amount',
                                     track_visibility='onchange')
    narration = fields.Char(string="Narration", required=True, readonly=True,
                            states={'draft': [('readonly', False)]}, track_visibility='onchange')
    narration_gl = fields.Char(string="Narration Gain/Loss", required=True, readonly=True,
                               states={'draft': [('readonly', False)]}, track_visibility='onchange')
    request_date = fields.Datetime(string='Request Date', required=True, default=fields.Datetime.now,
                                   readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    approve_date = fields.Datetime(string='Approve Date', readonly=True, states={'draft': [('readonly', False)]},
                                   track_visibility='onchange')
    dispose_date = fields.Datetime(string='Dispose Date', readonly=True, states={'approve': [('readonly', False)]},
                                   track_visibility='onchange')
    request_user_id = fields.Many2one('res.users', string='Request User', readonly=True,
                                      states={'draft': [('readonly', False)]}, default=lambda self: self.env.user,
                                      track_visibility='onchange')
    approve_user_id = fields.Many2one('res.users', string='Approve User', readonly=True,
                                      states={'draft': [('readonly', False)]}, track_visibility='onchange')
    dispose_user_id = fields.Many2one('res.users', string='Dispose User', readonly=True,
                                      states={'approve': [('readonly', False)]}, track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    note = fields.Text(string='Note', readonly=True, states={'draft': [('readonly', False)]},
                       track_visibility='onchange')
    line_ids = fields.One2many('account.asset.disposal.line', 'dispose_id', string='Disposal Line', readonly=True,
                               states={'draft': [('readonly', False)]}, track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('dispose', 'Disposed')], default='draft',
                             string='State', track_visibility='onchange')

    @api.depends('line_ids')
    def _compute_total_value(self):
        for rec in self:
            rec.total_value = sum(rec.cost_value for rec in rec.line_ids)

    @api.depends('line_ids')
    def _compute_total_depr_amount(self):
        for rec in self:
            rec.total_depr_amount = sum(rec.depreciation_value for rec in rec.line_ids)

    @api.one
    def action_approve(self):
        if len(self.line_ids) <= 0:
            raise Warning(_('[Warning] Dispose List should not be empty.'))

        if self.state == 'draft':
            self.write({
                'name': self.env['ir.sequence'].next_by_code('account.asset.disposal') or _('New'),
                'state': 'approve',
                'approve_date': fields.Datetime.now(),
                'approve_user_id': self.env.user.id,
            })

    @api.one
    def action_dispose(self):
        if self.state == 'approve':
            for rec in self.line_ids:
                date = datetime.strptime(fields.Datetime.now()[:10], DATE_FORMAT)
                dispose = self.generate_move(rec.asset_id)
                if dispose.state == 'draft':
                    dispose.sudo().post()
                    rec.write({'journal_entry': 'post', 'move_id': dispose.id})
                    response = rec.asset_id.set_to_close(date)

            self.write({
                'state': 'dispose',
                'dispose_date': fields.Datetime.now(),
                'dispose_user_id': self.env.user.id,
            })

    def generate_move(self, asset):
        prec = self.env['decimal.precision'].precision_get('Account')
        company_currency = asset.company_id.currency_id
        current_currency = asset.currency_id

        credit = {
            'name': self.narration,
            'account_id': asset.asset_type_id.account_asset_id.id,
            'credit': asset.value if float_compare(asset.value, 0.0, precision_digits=prec) > 0 else 0.0,
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
            'debit': asset.accumulated_value if float_compare(asset.accumulated_value, 0.0,
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
            'debit': asset.value_residual if float_compare(asset.value_residual, 0.0,
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
            'date': fields.Datetime.now() or False,
            'journal_id': asset.category_id.journal_id.id,
            'operating_unit_id': asset.current_branch_id.id,
            'sub_operating_unit_id': asset.sub_operating_unit_id.id,
            'line_ids': [(0, 0, credit), (0, 0, debit), (0, 0, debit2)],
        })

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'dispose'):
                raise Warning(_('[Warning] Approved and Disposed Record cannot deleted.'))
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

