# -*- coding: utf-8 -*-

from psycopg2 import IntegrityError

from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError


class AccountAssetCategory(models.Model):
    _name = 'account.asset.category'
    _inherit = ['account.asset.category', 'mail.thread']
    _order = 'code ASC'

    code = fields.Char(string='Code', size=4)
    active = fields.Boolean(default=True, track_visibility='onchange')
    name = fields.Char(required=True, index=True, string="Asset Type", size=50, track_visibility='onchange')
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, track_visibility='onchange')
    method_period = fields.Integer(string='One Entry Every', default=1, track_visibility='onchange',
                                   help="State here the time between 2 depreciations, in months", required=True)
    is_custom_depr = fields.Boolean(default=True, required=True)
    prorata = fields.Boolean(string='Prorata Temporis', default=True)
    depreciation_year = fields.Integer(string='Asset Life (In Year)', required=True, default=1,
                                       track_visibility='onchange')
    method_number = fields.Integer(string='Number of Depreciations', default=1,
                                   help="The number of depreciations needed to depreciate your asset")
    method = fields.Selection([('linear', 'Straight Line/Linear'), ('degressive', 'Reducing Method')],
                              string='Computation Method', required=True, default='linear', track_visibility='onchange',
                              help="Choose the method to use to compute the amount of depreciation lines.\n"
                                   "  * Linear: Calculated on basis of: Gross Value - Salvage Value/ Useful life of the fixed asset\n"
                                   "  * Reducing Method: Calculated on basis of: Residual Value * Depreciation Factor")
    account_asset_id = fields.Many2one('account.account', string='Asset Account', required=True,
                                       track_visibility='onchange',
                                       domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)],
                                       help="Account used to record the purchase of the asset at its original price.")
    asset_suspense_account_id = fields.Many2one('account.account', string='Asset Suspense Account', required=True,
                                                domain=[('deprecated', '=', False)], track_visibility='onchange')
    account_depreciation_id = fields.Many2one('account.account', required=True, track_visibility='onchange',
                                              domain=[('deprecated', '=', False)],
                                              string='Accumulated Depreciation A/C', )
    account_depreciation_expense_id = fields.Many2one('account.account', string='Depreciation Exp. A/C',
                                                      track_visibility='onchange',
                                                      required=True, domain=[('internal_type', '=', 'other'),
                                                                             ('deprecated', '=', False)],
                                                      oldname='account_income_recognition_id',
                                                      help="Account used in the periodical entries, to record a part of the asset as expense.")
    account_asset_loss_id = fields.Many2one('account.account', required=True, track_visibility='onchange',
                                            domain=[('deprecated', '=', False)],
                                            string='Asset Loss A/C')
    account_asset_gain_id = fields.Many2one('account.account', required=True, track_visibility='onchange',
                                            domain=[('deprecated', '=', False)],
                                            string='Asset Gain A/C')
    asset_sale_suspense_account_id = fields.Many2one('account.account', required=True, track_visibility='onchange',
                                                     domain=[('deprecated', '=', False)],
                                                     string='Asset Sales Suspense Account')

    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange', readonly=True,
                             states={'draft': [('readonly', False)]})
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approve'), ('reject', 'Reject')], default='draft',
                             track_visibility='onchange', )
    line_ids = fields.One2many('history.account.asset.category', 'line_id', string='Lines', readonly=True,
                               states={'draft': [('readonly', False)]})

    @api.model
    def create(self, vals):
        if 'parent_id' not in vals:
            if vals.get('code', 'New') == 'New':
                seq = self.env['ir.sequence']
                vals['code'] = seq.next_by_code('account.asset.type') or ''
        return super(AccountAssetCategory, self).create(vals)

    @api.onchange('depreciation_year')
    def onchange_depreciation_year(self):
        if self.depreciation_year:
            self.method_number = int(12 * self.depreciation_year)

    @api.constrains('depreciation_year')
    def check_depreciation_year(self):
        if self.depreciation_year < 1:
            raise ValidationError(_('Total year cannot be zero or negative value.'))

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.search(
                [('name', '=ilike', self.name.strip()), '|', ('active', '=', True), ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.one
    def name_get(self):
        if self.parent_id:
            name = '%s' % (self.name)
        else:
            name = '[%s] %s' % (self.code, self.name)
        return (self.id, name)

    @api.onchange("name")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()

    @api.one
    def act_draft(self):
        if self.state == 'approve':
            self.write({
                'state': 'draft'
            })

    @api.one
    def act_approve(self):
        if self.state == 'draft':
            self.write({
                'state': 'approve',
                'pending': False,
                'active': True,
            })

    @api.one
    def act_reject(self):
        if self.state == 'draft':
            self.write({
                'state': 'reject',
                'pending': False,
                'active': False,
            })

    @api.one
    def act_approve_pending(self):
        if self.pending == True:
            requested = self.line_ids.search([('state', '=', 'pending'), ('line_id', '=', self.id)], order='id desc',
                                             limit=1)
            if requested:
                self.write({
                    'name': self.name if not requested.change_name else requested.change_name,
                    'pending': False,
                    'active': requested.status,
                })
                requested.write({
                    'state': 'approve',
                    'change_date': fields.Datetime.now()
                })

    @api.one
    def act_reject_pending(self):
        if self.pending == True:
            requested = self.line_ids.search([('state', '=', 'pending'), ('line_id', '=', self.id)], order='id desc',
                                             limit=1)
            if requested:
                self.write({
                    'pending': False
                })
                requested.write({
                    'state': 'reject',
                    'change_date': fields.Datetime.now()
                })

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'reject'):
                raise ValidationError(_('[Warning] Approves and Rejected record cannot be deleted.'))

            try:
                return super(AccountAssetCategory, rec).unlink()
            except IntegrityError:
                raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                        "- deletion: you may be trying to delete a record while other records still reference it"))


class HistoryAccountAssetCategory(models.Model):
    _name = 'history.account.asset.category'
    _description = 'History Account Asset Category'
    _order = 'id desc'

    change_name = fields.Char('Proposed Name', size=50, readonly=True, states={'draft': [('readonly', False)]})
    status = fields.Boolean('Active', default=True, track_visibility='onchange')
    request_date = fields.Datetime(string='Requested Date')
    change_date = fields.Datetime(string='Approved Date')
    line_id = fields.Many2one('account.asset.category', ondelete='restrict')
    state = fields.Selection([('pending', 'Pending'), ('approve', 'Approved'), ('reject', 'Rejected')],
                             default='pending')
