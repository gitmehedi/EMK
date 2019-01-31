# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountAssetSale(models.Model):
    _name = 'account.asset.sale'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'
    _rec_name = 'name'

    name = fields.Char(string='Serial No', readonly=True, default='New')
    total_value = fields.Float(string='Total Asset Value', compute='_compute_total_value')
    total_sale_amount = fields.Float(string='Total Sale Value', compute='_compute_total_sale_amount')
    request_date = fields.Datetime(string='Request Date', required=True, default=fields.Datetime.now(),
                                   readonly=True, states={'draft': [('readonly', False)]})
    approve_date = fields.Datetime(string='Approve Date', readonly=True, states={'draft': [('readonly', False)]})
    sale_date = fields.Datetime(string='Dispose Date', readonly=True, states={'approve': [('readonly', False)]})
    request_user_id = fields.Many2one('res.users', string='Request User', readonly=True,
                                      states={'draft': [('readonly', False)]}, default=lambda self: self.env.user)
    approve_user_id = fields.Many2one('res.users', string='Approve User', readonly=True,
                                      states={'draft': [('readonly', False)]}, )
    sale_user_id = fields.Many2one('res.users', string='Dispose User', readonly=True,
                                   states={'approve': [('readonly', False)]}, )
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    note = fields.Text(string='Note', readonly=True, states={'draft': [('readonly', False)]}, )

    line_ids = fields.One2many('account.asset.sale.line', 'sale_id', string='Sale Line', readonly=True,
                               states={'draft': [('readonly', False)]}, )
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('sale', 'Sold')], default='draft',
                             string='State')

    @api.depends('line_ids')
    def _compute_total_value(self):
        for rec in self:
            rec.total_value = sum(rec.asset_value for rec in rec.line_ids)

    @api.depends('line_ids')
    def _compute_total_sale_amount(self):
        for rec in self:
            rec.total_sale_amount = sum(rec.sale_value for rec in rec.line_ids)

    @api.one
    def action_approve(self):
        if len(self.line_ids) <= 0:
            raise ValidationError(_("Sale List should not empty."))

        if self.state == 'draft':
            self.state = 'approve'
            self.approve_date = fields.Datetime.now()
            self.approve_user_id = self.env.user.id
            self.name = self.env['ir.sequence'].next_by_code('account.asset.sale') or _('New')

    @api.one
    def action_sale(self):
        if self.state == 'approve':
            for rec in self.line_ids:
                rec.asset_id.set_to_close()
                for depr in rec.asset_id.depreciation_line_ids:
                    if depr.move_id.state == 'draft':
                        depr.move_id.post()
                rec.journal_entry='post'

            self.state = 'sale'
            self.sale_date = fields.Datetime.now()
            self.sale_user_id = self.env.user.id

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'sale'):
                raise ValidationError(_('Record cannot delete after approval.'))
        return super(AccountAssetSale, self).unlink()


class AccountAssetSaleLine(models.Model):
    _name = 'account.asset.sale.line'
    _rec = 'id ASC'

    asset_id = fields.Many2one('account.asset.asset', required=True, string='Asset Name')
    asset_value = fields.Float(string='Asset Value', required=True, digits=(14, 2))
    depreciation_value = fields.Float(string='Depreciation Value', required=True, digits=(14, 2))
    sale_value = fields.Float(string='Sale Value', required=True, digits=(14, 2))

    sale_id = fields.Many2one('account.asset.sale', string='Sale', ondelete='restrict')
    journal_entry = fields.Selection([('unpost', 'Unposted'), ('post', 'Posted')], default='unpost', requried=True)

    @api.onchange('asset_id')
    def onchange_asset(self):
        if self.asset_id:
            self.asset_value = self.asset_id.value_residual
            self.depreciation_value = self.asset_id.value - self.asset_id.value_residual
