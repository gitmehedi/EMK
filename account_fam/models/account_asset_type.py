# -*- coding: utf-8 -*-

from psycopg2 import IntegrityError

from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError


class AccountAssetCategory(models.Model):
    _name = 'account.asset.category'
    _inherit = ['account.asset.category', 'mail.thread']
    _order = 'code ASC'

    code = fields.Char(string='Code', size=4, required=True)
    active = fields.Boolean(default=True, track_visibility='onchange')
    name = fields.Char(required=True, index=True, string="Asset Type", size=200, track_visibility='onchange')
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, track_visibility='onchange')
    method_period = fields.Integer(string='One Entry (In Month)', default=1, track_visibility='onchange',
                                   help="State here the time between 2 depreciations, in months", required=True)

    is_custom_depr = fields.Boolean(default=True, required=True)
    prorata = fields.Boolean(string='Prorata Temporis', default=True)
    depreciation_year = fields.Integer(string='Asset Life (In Year)', required=True, default=0,
                                       track_visibility='onchange')
    method_number = fields.Integer(string='Number of Depreciations', default=1,
                                   help="The number of depreciations needed to depreciate your asset")
    method = fields.Selection([('degressive', 'Reducing Method'), ('linear', 'Straight Line/Linear')],
                              string='Computation Method', required=True, default='degressive',
                              track_visibility='onchange',
                              help="Choose the method to use to compute the amount of depreciation lines.\n"
                                   "  * Linear: Calculated on basis of: Gross Value - Salvage Value/ Useful life of the fixed asset\n"
                                   "  * Reducing Method: Calculated on basis of: Residual Value * Depreciation Factor")
    account_asset_id = fields.Many2one('account.account', string='Asset Account', required=True,
                                       track_visibility='onchange',
                                       domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)],
                                       help="Account used to record the purchase of the asset at its original price.")
    asset_suspense_account_id = fields.Many2one('account.account', string='Asset Awaiting Allocation', required=True,
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
                                                     string='Asset Awaiting Disposal')

    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange', readonly=True,
                             states={'draft': [('readonly', False)]})
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Reject')], default='draft',
                             track_visibility='onchange', )
    line_ids = fields.One2many('history.account.asset.category', 'line_id', string='Lines', readonly=True,
                               states={'draft': [('readonly', False)]})


    @api.model
    def create(self, vals):
        return super(AccountAssetCategory, self).create(vals)

    @api.onchange('account_asset_id')
    def onchange_account_asset(self):
        return False

    @api.constrains('method')
    def check_method(self):
        if self.method == 'linear':
            if self.depreciation_year < 1:
                raise ValidationError(_('Asset Life (In Year) cann\'t be zero or negative value.'))
        else:
            if self.method_progress_factor <= 0:
                raise ValidationError(_('Depreciation Factor cann\'t be zero or negative value.'))

    @api.onchange('depreciation_year')
    def onchange_depreciation_year(self):
        if self.depreciation_year:
            self.method_number = int(12 * self.depreciation_year)

    @api.constrains('depreciation_year')
    def check_depreciation_year(self):
        if self.method == 'linear':
            if self.depreciation_year < 1:
                raise ValidationError(_('Total year cannot be zero or negative value.'))

    @api.onchange("code")
    def onchange_code(self):
        if self.code:
            filter = str(self.code.strip())
            if self.parent_id:
                self.code = self.parent_id.code + filter[2:]
            elif not self.parent_id:
                self.code = filter

    @api.constrains('name', 'code')
    def _check_unique_constrain(self):
        if self.name:
            if self.parent_id:
                name = self.search(
                    [('name', '=ilike', self.name.strip()), ('parent_id', '!=', None), '|', ('active', '=', True),
                     ('active', '=', False)])
            else:
                name = self.search(
                    [('name', '=ilike', self.name.strip()), ('parent_id', '=', None), '|', ('active', '=', True),
                     ('active', '=', False)])

            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

        if self.code:
            if self.parent_id and (len(self.code) != 4 or not self.code.isdigit()):
                raise Warning(_('[Value Error] Code must be 4 digit!'))
            elif not self.parent_id and (len(self.code) != 2 or not self.code.isdigit()):
                raise Warning(_('[Value Error] Code must be 2 digit!'))

            if self.parent_id:
                code = self.search(
                    [('code', '=ilike', self.code.strip()), ('parent_id', '!=', None), '|', ('active', '=', True),
                     ('active', '=', False)], )
            else:
                code = self.search(
                    [('code', '=ilike', self.code.strip()), ('parent_id', '=', None), '|', ('active', '=', True),
                     ('active', '=', False)])

            if len(code) > 1:
                raise Warning('[Unique Error] Code must be unique!')

    @api.onchange('type')
    def onchange_type(self):
        if self.type == 'sale':
            self.prorata = True
            self.method_period = 1
        else:
            self.method_period = 1

    @api.one
    def name_get(self):
        if self.code:
            name = '[%s] %s' % (self.code, self.name)
        return (self.id, name)

    @api.onchange("name")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()

    @api.one
    def act_draft(self):
        if self.state == 'reject':
            self.write({
                'state': 'draft',
                'pending': True,
                'active': False,
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
                    'method_progress_factor': requested.method_progress_factor,
                    'journal_id': requested.journal_id.id,
                    'depreciation_year': requested.depreciation_year,
                    'method_number': requested.method_number,
                    'method': requested.method,
                    'account_asset_id': requested.account_asset_id.id,
                    'asset_suspense_account_id': requested.asset_suspense_account_id.id,
                    'account_depreciation_id': requested.account_depreciation_id.id,
                    'account_depreciation_expense_id': requested.account_depreciation_expense_id.id,
                    'account_asset_loss_id': requested.account_asset_loss_id.id,
                    'account_asset_gain_id': requested.account_asset_gain_id.id,
                    'asset_sale_suspense_account_id': requested.asset_sale_suspense_account_id.id,
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

    change_name = fields.Char('Proposed Name', size=200, readonly=True, states={'draft': [('readonly', False)]})
    status = fields.Boolean('Active', default=True, track_visibility='onchange')
    request_date = fields.Datetime(string='Requested Date')
    change_date = fields.Datetime(string='Approved Date')
    line_id = fields.Many2one('account.asset.category', ondelete='restrict')
    state = fields.Selection([('pending', 'Pending'), ('approve', 'Approved'), ('reject', 'Rejected')],
                             default='pending')
    method_progress_factor = fields.Float(string='Depreciation Factor', default=0.0, )
    journal_id = fields.Many2one('account.journal', string='Journal')
    depreciation_year = fields.Integer(string='Asset Life (In Year)', default=0)
    method_number = fields.Integer(string='Number of Depreciations', default=0)
    method = fields.Selection([('degressive', 'Reducing Method'), ('linear', 'Straight Line/Linear')],
                              string='Computation Method', default='degressive')
    account_asset_id = fields.Many2one('account.account', string='Asset Account',
                                       domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)])
    asset_suspense_account_id = fields.Many2one('account.account', string='Asset Awaiting Allocation',
                                                domain=[('deprecated', '=', False)])
    account_depreciation_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)],
                                              string='Accumulated Depreciation A/C', )
    account_depreciation_expense_id = fields.Many2one('account.account', string='Depreciation Exp. A/C',
                                                      domain=[('internal_type', '=', 'other'),
                                                              ('deprecated', '=', False)])
    account_asset_loss_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)],
                                            string='Asset Loss A/C')
    account_asset_gain_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)],
                                            string='Asset Gain A/C')
    asset_sale_suspense_account_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)],
                                                     string='Asset Awaiting Disposal')
