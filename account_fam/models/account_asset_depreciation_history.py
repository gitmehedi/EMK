# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import Warning, ValidationError

DATE_FORMAT = "%Y-%m-%d"


class AccountAssetDepreciationHistory(models.Model):
    _name = 'account.asset.depreciation.history'
    _description = 'Depreciation History'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'
    _rec_name = 'date'

    date = fields.Date(string='Depreciation Date', required=True, readonly=True)
    total_amount = fields.Float(compute='_compute_total_amount', string='Amount', store=True)
    request_date = fields.Date(string='Request Date', required=True,
                               default=lambda self: self.env.user.company_id.batch_date,
                               readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    approve_date = fields.Date(string='Approve Date', readonly=True, states={'draft': [('readonly', False)]},
                               track_visibility='onchange')
    request_user_id = fields.Many2one('res.users', string='Request User', readonly=True,
                                      states={'draft': [('readonly', False)]}, default=lambda self: self.env.user,
                                      track_visibility='onchange')
    approve_user_id = fields.Many2one('res.users', string='Approve User', readonly=True,
                                      states={'draft': [('readonly', False)]}, track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    line_ids = fields.One2many('account.asset.depreciation.history.line', 'line_id', string='Lines')
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved')], default='draft',
                             string='Status', track_visibility='onchange')

    @api.multi
    @api.depends('line_ids')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = sum([val.amount for val in rec.line_ids])

    @api.multi
    def action_approve(self):
        if self.env.user.id == self.request_user_id.id and self.env.user.id != SUPERUSER_ID:
            raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))
        post = True
        if self.state == 'draft':
            for rec in self.line_ids:
                move = rec.journal_id
                if move.state == 'draft':
                    if move.name == '/':
                        sequence = move.journal_id.sequence_id
                        new_name = sequence.with_context(ir_sequence_date=move.date).next_by_id()
                        move.write({
                            'name': new_name,
                            'maker_id': self.request_user_id.id,
                            'approver_id': self.env.user.id,
                            'is_cr': True,
                            'state': 'posted',
                        })
                else:
                    post = False

            if post:
                self.write({
                    'state': 'approve',
                    'approve_date': self.env.user.company_id.batch_date,
                    'approve_user_id': self.env.user.id
                })

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('draft', 'approve'):
                raise Warning(_('[Warning] Approved and Disposed Record cannot deleted.'))
        return super(AccountAssetDepreciationHistory, self).unlink()

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'draft')]


class AccountAssetDepreciationHistory(models.Model):
    _name = 'account.asset.depreciation.history.line'

    journal_id = fields.Many2one('account.move', string='Journal', required=True)
    amount = fields.Float(string='Amount', required=True)
    line_id = fields.Many2one('account.asset.depreciation.history', string='Journal')
