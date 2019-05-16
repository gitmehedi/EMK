# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountAssetDisposal(models.Model):
    _name = 'account.asset.disposal'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'name desc,id desc'
    _rec_name = 'name'

    name = fields.Char(string='Serial No', readonly=True, default='New')
    total_value = fields.Float(string='Asset Value', compute='_compute_total_value')
    total_depr_amount = fields.Float(string='Depreciation Value', compute='_compute_total_depr_amount')
    request_date = fields.Datetime(string='Request Date', required=True, default=fields.Datetime.now(),
                                   readonly=True, states={'draft': [('readonly', False)]})
    approve_date = fields.Datetime(string='Approve Date', readonly=True, states={'draft': [('readonly', False)]})
    dispose_date = fields.Datetime(string='Dispose Date', readonly=True, states={'approve': [('readonly', False)]})
    request_user_id = fields.Many2one('res.users', string='Request User', readonly=True,
                                      states={'draft': [('readonly', False)]}, default=lambda self: self.env.user)
    approve_user_id = fields.Many2one('res.users', string='Approve User', readonly=True,
                                      states={'draft': [('readonly', False)]}, )
    dispose_user_id = fields.Many2one('res.users', string='Dispose User', readonly=True,
                                      states={'approve': [('readonly', False)]}, )
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    note = fields.Text(string='Note', readonly=True, states={'draft': [('readonly', False)]}, )
    line_ids = fields.One2many('account.asset.disposal.line', 'dispose_id', string='Disposal Line' )
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('dispose', 'Disposed')], default='draft',
                             string='State')

    @api.depends('line_ids')
    def _compute_total_value(self):
        for rec in self:
            rec.total_value = sum(rec.asset_value for rec in rec.line_ids)

    @api.depends('line_ids')
    def _compute_total_depr_amount(self):
        for rec in self:
            rec.total_depr_amount = sum(rec.depreciation_value for rec in rec.line_ids)

    @api.one
    def action_approve(self):
        if len(self.line_ids) <= 0:
            raise ValidationError(_("Dispose List should not empty."))

        if self.state == 'draft':
            self.state = 'approve'
            self.approve_date = fields.Datetime.now()
            self.approve_user_id = self.env.user.id
            self.name = self.env['ir.sequence'].next_by_code('account.asset.disposal') or _('New')

    @api.one
    def action_dispose(self):
        if self.state == 'approve':
            for rec in self.line_ids:
                rec.asset_id.set_to_close()
                for depr in rec.asset_id.depreciation_line_ids:
                    if depr.move_id.state == 'draft':
                        depr.move_id.post()
                rec.journal_entry='post'

            self.state = 'dispose'
            self.dispose_date = fields.Datetime.now()
            self.dispose_user_id = self.env.user.id

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'dispose'):
                raise ValidationError(_('Record cannot delete after approval.'))
        return super(AccountAssetDisposal, self).unlink()

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'approve')]


class AccountAssetDisposalLine(models.Model):
    _name = 'account.asset.disposal.line'
    _rec = 'id ASC'

    asset_id = fields.Many2one('account.asset.asset', required=True, string='Asset Name')
    asset_value = fields.Float(string='Asset Value', required=True, digits=(14, 2))
    depreciation_value = fields.Float(string='Depreciation Value', required=True, digits=(14, 2))

    dispose_id = fields.Many2one('account.asset.disposal', string='Disposal', ondelete='restrict')
    journal_entry = fields.Selection([('unpost', 'Unposted'), ('post', 'Posted')], default='unpost', requried=True)

    @api.onchange('asset_id')
    def onchange_asset(self):
        if self.asset_id:
            self.asset_value = self.asset_id.value_residual
            self.depreciation_value = self.asset_id.value - self.asset_id.value_residual
