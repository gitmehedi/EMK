# -*- coding: utf-8 -*-

from psycopg2 import IntegrityError

from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import Warning, ValidationError


class AccountAssetCategory(models.Model):
    _name = 'account.asset.category'
    _inherit = ['account.asset.category', 'mail.thread']
    _order = 'code ASC'

    code = fields.Char(string='Code', size=4, required=True)
    active = fields.Boolean(default=True, track_visibility='onchange')
    name = fields.Char(required=True, index=True, string="Asset Type", size=200, track_visibility='onchange')
    journal_id = fields.Many2one('account.journal', string='Journal', readonly=True,
                                 default=lambda self: self.env.user.company_id.fa_journal_id.id, required=True,
                                 track_visibility='onchange')
    method_period = fields.Integer(string='One Entry (In Month)', default=1, track_visibility='onchange',
                                   help="State here the time between 2 depreciations, in months", required=True)

    is_custom_depr = fields.Boolean(default=True, required=True)
    prorata = fields.Boolean(string='Prorata Temporis', default=True)
    depreciation_year = fields.Integer(string='Asset Life (In Year)', required=True, default=0,
                                       track_visibility='onchange')
    method_number = fields.Integer(string='Number of Depreciations', default=1,
                                   help="The number of depreciations needed to depreciate your asset")
    method = fields.Selection([('degressive', 'Reducing Method'),
                               ('linear', 'Straight Line/Linear'),
                               ('no_depreciation', 'No Depreciation')],
                              string='Computation Method', required=True, default='degressive',
                              track_visibility='onchange')
    account_asset_id = fields.Many2one('account.account', string='Asset Account', required=True,
                                       track_visibility='onchange',
                                       domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)])
    account_asset_seq_id = fields.Many2one('sub.operating.unit', string='Asset Account Sequence', required=True,
                                           track_visibility='onchange', )
    asset_suspense_account_id = fields.Many2one('account.account', string='Asset Awaiting Allocation', required=True,
                                                domain=[('deprecated', '=', False)], track_visibility='onchange')
    asset_suspense_seq_id = fields.Many2one('sub.operating.unit', string='Asset Awaiting Allocation Sequence',
                                            required=True, track_visibility='onchange', )
    account_depreciation_id = fields.Many2one('account.account', track_visibility='onchange', required=False,
                                              domain=[('deprecated', '=', False)],
                                              string='Accumulated Depreciation A/C', )
    account_depreciation_seq_id = fields.Many2one('sub.operating.unit', string='Accumulated Depreciation A/C Sequence',
                                                  required=False, track_visibility='onchange', )
    account_depreciation_expense_id = fields.Many2one('account.account', string='Depreciation Exp. A/C',
                                                      track_visibility='onchange', required=False,
                                                      domain=[('internal_type', '=', 'other'),('deprecated', '=', False)])
    account_depreciation_expense_seq_id = fields.Many2one('sub.operating.unit', string='Depreciation Exp. A/C Sequence',
                                                          required=False, track_visibility='onchange', )
    account_asset_loss_id = fields.Many2one('account.account', required=True, track_visibility='onchange',
                                            domain=[('deprecated', '=', False)],string='Asset Loss A/C')
    account_asset_loss_seq_id = fields.Many2one('sub.operating.unit', string='Asset Loss A/C Sequence', required=True,
                                                track_visibility='onchange', )
    account_asset_gain_id = fields.Many2one('account.account', required=True, track_visibility='onchange',
                                            domain=[('deprecated', '=', False)],string='Asset Gain A/C')
    account_asset_gain_seq_id = fields.Many2one('sub.operating.unit', string='Asset Gain A/C Sequence', required=True,
                                                track_visibility='onchange', )
    asset_sale_suspense_account_id = fields.Many2one('account.account', required=True, track_visibility='onchange',
                                                     domain=[('deprecated', '=', False)],string='Asset Awaiting Disposal')
    asset_sale_suspense_seq_id = fields.Many2one('sub.operating.unit', string='Asset Awaiting Disposal Sequence',
                                                 required=True, track_visibility='onchange' )

    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange', readonly=True,
                             states={'draft': [('readonly', False)]})
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Reject')], default='draft',
                             track_visibility='onchange', )
    line_ids = fields.One2many('history.account.asset.category', 'line_id', string='Lines', readonly=True,
                               states={'draft': [('readonly', False)]})
    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user.id, track_visibility='onchange')
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange')
    asset_count = fields.Integer(default=0)

    @api.model
    def create(self, vals):
        return super(AccountAssetCategory, self).create(vals)

    @api.onchange('account_asset_id')
    def onchange_account_asset(self):
        return False

    @api.onchange('account_asset_id')
    def _onchange_account_asset_id(self):
        for rec in self:
            rec.account_asset_seq_id = None

    @api.onchange('asset_suspense_account_id')
    def _onchange_asset_suspense_account_id(self):
        for rec in self:
            rec.asset_suspense_seq_id = None

    @api.onchange('account_depreciation_expense_id')
    def _onchange_account_depreciation_expense_id(self):
        for rec in self:
            rec.account_depreciation_expense_seq_id = None

    @api.onchange('account_depreciation_id')
    def _onchange_account_depreciation_id(self):
        for rec in self:
            rec.account_depreciation_seq_id = None

    @api.onchange('account_asset_loss_id')
    def _onchange_account_asset_loss_id(self):
        for rec in self:
            rec.account_asset_loss_seq_id = None

    @api.onchange('account_asset_gain_id')
    def _onchange_account_asset_gain_id(self):
        for rec in self:
            rec.account_asset_gain_seq_id = None

    @api.onchange('asset_sale_suspense_account_id')
    def _onchange_asset_sale_suspense_account_id(self):
        for rec in self:
            rec.asset_sale_suspense_seq_id = None

    @api.constrains('method')
    def check_method(self):
        if self.method == 'linear':
            if self.depreciation_year < 1:
                raise ValidationError(_('Asset Life (In Year) cann\'t be zero or negative value.'))
        if self.method == 'degressive':
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
                raise ValidationError(_('Asset Life cann\'t be zero or negative value.'))

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
                    [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), ('parent_id', '!=', None), '|',
                     ('active', '=', True), ('active', '=', False)])
            else:
                name = self.search(
                    [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), ('parent_id', '=', None), '|',
                     ('active', '=', True), ('active', '=', False)])

            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

        if self.code:
            if self.parent_id and (len(self.code) != 4 or not self.code.isdigit()):
                raise Warning(_('[Value Error] Code must be 4 digit!'))
            elif not self.parent_id and (len(self.code) != 2 or not self.code.isdigit()):
                raise Warning(_('[Value Error] Code must be 2 digit!'))

            if self.parent_id:
                code = self.search(
                    [('code', '=ilike', self.code.strip()), ('state', '!=', 'reject'), ('parent_id', '!=', None), '|',
                     ('active', '=', True), ('active', '=', False)])
            else:
                code = self.search(
                    [('code', '=ilike', self.code.strip()), ('state', '!=', 'reject'), ('parent_id', '=', None), '|',
                     ('active', '=', True), ('active', '=', False)])

            if len(code) > 1:
                raise Warning('[Unique Error] Code must be unique!')

    @api.onchange('type')
    def onchange_type(self):
        if self.type == 'sale':
            self.prorata = True
            self.method_period = 1
        else:
            self.method_period = 1

    @api.onchange('method')
    def onchange_method(self):
        if self.method == 'no_depreciation':
            self.account_depreciation_expense_id = None
            self.account_depreciation_id = None

    @api.one
    def name_get(self):
        if self.code:
            name = '[%s] %s' % (self.code, self.name)
        return (self.id, name)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        names1 = super(models.Model, self).name_search(name=name, args=args, operator=operator, limit=limit)
        names2 = []
        if name:
            domain = ['|', ('code', '=', name), ('name', '=', name + '%')]
            names2 = self.search(domain, limit=limit).name_get()
        return list(set(names1) | set(names2))[:limit]

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
        if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
            raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))
        if self.state == 'draft':
            self.write({
                'state': 'approve',
                'pending': False,
                'active': True,
                'approver_id': self.env.user.id,
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
        if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
            raise ValidationError(_("[Validation Error] Editor and Approver can't be same person!"))
        if self.pending == True:
            requested = self.line_ids.search([('state', '=', 'pending'), ('line_id', '=', self.id)], order='id desc',
                                             limit=1)
            if requested:
                line = {
                    'name': self.name if not requested.change_name else requested.change_name,
                    'pending': False,
                    'active': requested.status,
                    'approver_id': self.env.user.id,
                }

                if requested.method_progress_factor:
                    line['method_progress_factor'] = requested.method_progress_factor
                if requested.depreciation_year:
                    line['depreciation_year'] = requested.depreciation_year
                if requested.method_number:
                    line['method_number'] = requested.method_number
                if requested.method:
                    line['method'] = requested.method
                if requested.journal_id:
                    line['journal_id'] = requested.journal_id.id

                if requested.account_asset_id:
                    line['account_asset_id'] = requested.account_asset_id.id
                if requested.asset_suspense_account_id:
                    line['asset_suspense_account_id'] = requested.asset_suspense_account_id.id
                if requested.account_depreciation_id:
                    line['account_depreciation_id'] = requested.account_depreciation_id.id
                if requested.account_depreciation_expense_id:
                    line['account_depreciation_expense_id'] = requested.account_depreciation_expense_id.id
                if requested.account_asset_loss_id:
                    line['account_asset_loss_id'] = requested.account_asset_loss_id.id
                if requested.account_asset_gain_id:
                    line['account_asset_gain_id'] = requested.account_asset_gain_id.id
                if requested.asset_sale_suspense_account_id:
                    line['asset_sale_suspense_account_id'] = requested.asset_sale_suspense_account_id.id

                if requested.account_asset_seq_id:
                    line['account_asset_seq_id'] = requested.account_asset_seq_id.id
                if requested.asset_suspense_seq_id:
                    line['asset_suspense_seq_id'] = requested.asset_suspense_seq_id.id
                if requested.account_depreciation_seq_id:
                    line['account_depreciation_seq_id'] = requested.account_depreciation_seq_id.id
                if requested.account_depreciation_seq_id:
                    line['account_depreciation_expense_seq_id'] = requested.account_depreciation_expense_seq_id.id
                if requested.account_asset_loss_seq_id:
                    line['account_asset_loss_seq_id'] = requested.account_asset_loss_seq_id.id
                if requested.account_asset_gain_seq_id:
                    line['account_asset_gain_seq_id'] = requested.account_asset_gain_seq_id.id
                if requested.asset_sale_suspense_seq_id:
                    line['asset_sale_suspense_seq_id'] = requested.asset_sale_suspense_seq_id.id

                self.write(line)
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
    method_progress_factor = fields.Float(string='Depreciation Factor', digits=(1, 3), default=0.0, )
    journal_id = fields.Many2one('account.journal', string='Journal')
    depreciation_year = fields.Integer(string='Asset Life (In Year)', default=0)
    method_number = fields.Integer(string='Number of Depreciations', default=0)
    method = fields.Selection([('degressive', 'Reducing Method'),
                               ('linear', 'Straight Line/Linear'),
                               ('no_depreciation', 'No Depreciation')],
                              string='Computation Method', default='degressive')
    account_asset_id = fields.Many2one('account.account', string='Asset Account',
                                       domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)])
    asset_suspense_account_id = fields.Many2one('account.account', string='Asset Awaiting Allocation',
                                                domain=[('deprecated', '=', False)])
    account_depreciation_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)],
                                              string='Accumulated Depreciation A/C', required=False)
    account_depreciation_expense_id = fields.Many2one('account.account', string='Depreciation Exp. A/C',
                                                      domain=[('internal_type', '=', 'other'),
                                                              ('deprecated', '=', False)], required=False)
    account_asset_loss_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)],
                                            string='Asset Loss A/C')
    account_asset_gain_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)],
                                            string='Asset Gain A/C')
    asset_sale_suspense_account_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)],
                                                     string='Asset Awaiting Disposal')
    account_asset_seq_id = fields.Many2one('sub.operating.unit', string='Asset Account Sequence')
    asset_suspense_seq_id = fields.Many2one('sub.operating.unit', string='Asset Awaiting Allocation Sequence')
    account_depreciation_seq_id = fields.Many2one('sub.operating.unit', string='Accumulated Depreciation A/C Sequence')
    account_depreciation_expense_seq_id = fields.Many2one('sub.operating.unit', string='Depreciation Exp. A/C Sequence')
    account_asset_loss_seq_id = fields.Many2one('sub.operating.unit', string='Asset Loss A/C Sequence')
    account_asset_gain_seq_id = fields.Many2one('sub.operating.unit', string='Asset Gain A/C Sequence')
    asset_sale_suspense_seq_id = fields.Many2one('sub.operating.unit', string='Asset Awaiting Disposal Sequence')
