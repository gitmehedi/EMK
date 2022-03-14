# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import Warning, ValidationError
from psycopg2 import IntegrityError


class AccountAccount(models.Model):
    _name = 'account.account'
    _inherit = ['account.account', 'mail.thread', 'ir.needaction_mixin']
    _order = 'code,state asc'
    _description = 'Chart of Account'

    name = fields.Char(size=200, track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    code = fields.Char(size=8, track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    parent_id = fields.Many2one(track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    user_type_id = fields.Many2one(track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one(track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    deprecated = fields.Boolean(track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    reconcile = fields.Boolean(track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    level_size = fields.Integer(related='level_id.size')

    level_id = fields.Many2one('account.account.level', ondelete='restrict', string='Layer', required=True,
                               track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange', readonly=True,
                             states={'draft': [('readonly', False)]})
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             track_visibility='onchange', string='Status')
    line_ids = fields.One2many('history.account.account', 'line_id', string='Lines', readonly=True,
                               states={'draft': [('readonly', False)]})
    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user.id, track_visibility='onchange')
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange')
    gl_type = fields.Selection([('online', 'Online')], string='GL Type', readonly=True,
                               states={'draft': [('readonly', False)]})
    originating_type = fields.Selection([('debit', 'Originating Debit'), ('credit', 'Originating Credit')],
                                        string='Originating Type', readonly=True,
                                        states={'draft': [('readonly', False)]})
    tb_filter = fields.Boolean(string="TB Filter", default=False, readonly=True,
                               states={'draft': [('readonly', False)]})
    tpm_currency_id = fields.Many2one('res.currency', string='TPM Currency', readonly=True,
                                      states={'draft': [('readonly', False)]})

    @api.constrains('code')
    def _check_numeric_constrain(self):
        if self.code and not self.code.isdigit():
            raise Warning(_('[Format Error] Code must be numeric!'))
        if self.level_id.size != len(self.code):
            raise Warning(_('[Value Error] Code must be {0} digit!'.format(self.level_id.size)))

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.search(
                [('name', '=ilike', self.name.strip()),
                 ('level_id', '=', self.level_id.id),
                 ('parent_id', '=', self.parent_id.id),
                 ('state', '!=', 'reject'),
                 '|', ('active', '=', True), ('active', '=', False)])
            if len(name) > 1:
                raise Warning(_('[Unique Error] Name must be unique!'))

    @api.onchange('reconcile')
    def onchange_originating_type(self):
        self.originating_type = False

    @api.onchange("level_id")
    def onchange_levels(self):
        if self.level_id:
            if self.level_id.name == 'Layer 1':
                parents = self.search([('level_id', '=', self.level_id.parent_id.id)])
                self.parent_id = parents.id
            else:
                res = {}
                self.parent_id = None
                self.code = None
                self.name = None
                self.user_type_id = None
                parents = self.search([('level_id', '=', self.level_id.parent_id.id)])
                res['domain'] = {
                    'parent_id': [('id', 'in', parents.ids)],
                }
                return res

    @api.onchange("parent_id")
    def onchange_strips(self):
        if self.parent_id:
            self.code = self.parent_id.code

    @api.model
    def name_search(self, name, args=None, operator='=ilike', limit=100):
        limit = 100
        default, values, domain = [], [], []
        context = self.env.context

        if name:
            if 'show_parent_account' in context:
                domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            else:
                domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name),
                          ('level_id.name', '=', 'Layer 5')]
            values = self.search(domain, limit=limit, order='code ASC').name_get()
        else:
            if 'show_parent_account' not in context:
                domain = [('level_id.name', '=', 'Layer 5')]

            default = self.search(domain + args, limit=limit, order='code ASC').name_get()

        return list(set(default) | set(values))[:limit]

    @api.one
    def name_get(self):
        name = self.name
        if self.name and self.code:
            name = '[%s] %s' % (self.code, self.name)
        return (self.id, name)

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'draft')]

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
                change_val = {
                    'pending': False,
                    'active': requested.status,
                    'approver_id': self.env.user.id,
                }
                if requested.change_name:
                    change_val['name'] = requested.change_name
                if requested.user_type_id:
                    change_val['user_type_id'] = requested.user_type_id.id
                if requested.currency_id:
                    change_val['currency_id'] = requested.currency_id.id
                if requested.tpm_currency_id:
                    change_val['tpm_currency_id'] = requested.tpm_currency_id.id
                if self.reconcile != requested.reconcile:
                    change_val['reconcile'] = requested.reconcile
                if self.originating_type != requested.originating_type:
                    change_val['originating_type'] = requested.originating_type

                self.write(change_val)

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
                return super(AccountAccount, rec).unlink()
            except IntegrityError:
                raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                        "- deletion: you may be trying to delete a record while other records still reference it"))


class HistoryAccountAccount(models.Model):
    _name = 'history.account.account'
    _description = 'History Account Account'
    _order = 'id desc'

    change_name = fields.Char('Proposed Name', size=200, readonly=True, states={'draft': [('readonly', False)]})
    status = fields.Boolean('Active', default=True, track_visibility='onchange')
    request_date = fields.Datetime(string='Requested Date')
    change_date = fields.Datetime(string='Approved Date')
    line_id = fields.Many2one('account.account', ondelete='restrict')
    user_type_id = fields.Many2one('account.account.type', string='Type')
    currency_id = fields.Many2one('res.currency', string='Account Currency')
    tpm_currency_id = fields.Many2one('res.currency', string='TPM Currency')
    reconcile = fields.Boolean(string='Allow Reconciliation')
    state = fields.Selection([('pending', 'Pending'), ('approve', 'Approved'), ('reject', 'Rejected')],
                             default='pending', string='Status')
    originating_type = fields.Selection([('debit', 'Originating Debit'), ('credit', 'Originating Credit')],
                                        string='Originating Type')


class AccountAccountTag(models.Model):
    _name = 'account.account.tag'
    _order = 'name desc'
    _inherit = ['account.account.tag', 'mail.thread']
    _description = 'Account Tag'

    name = fields.Char('Name', required=True, size=200, track_visibility='onchange', readonly=True,
                       states={'draft': [('readonly', False)]})
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange', readonly=True,
                             states={'draft': [('readonly', False)]})
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status', track_visibility='onchange')
    line_ids = fields.One2many('history.account.tag', 'line_id', string='Lines', readonly=True,
                               states={'draft': [('readonly', False)]})

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
                return super(AccountAccountTag, rec).unlink()
            except IntegrityError:
                raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                        "- deletion: you may be trying to delete a record while other records still reference it"))

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.search(
                [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                 ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.onchange("name")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()

    @api.one
    def name_get(self):
        name = self.name
        if self.name:
            name = '%s' % (self.name)
        return (self.id, name)


class HistoryAccountTag(models.Model):
    _name = 'history.account.tag'
    _description = 'History Account Tag'
    _order = 'id desc'

    change_name = fields.Char('Proposed Name', size=200, readonly=True, states={'draft': [('readonly', False)]})
    status = fields.Boolean('Active', default=True, track_visibility='onchange')
    request_date = fields.Datetime(string='Requested Date')
    change_date = fields.Datetime(string='Approved Date')
    line_id = fields.Many2one('account.tag', ondelete='restrict')
    state = fields.Selection([('pending', 'Pending'), ('approve', 'Approved'), ('reject', 'Rejected')],
                             default='pending', string='Status')
