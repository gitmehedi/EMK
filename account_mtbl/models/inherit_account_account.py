# -*- coding: utf-8 -*-
from psycopg2 import IntegrityError

from odoo import api, fields, models, _
from odoo.exceptions import Warning, ValidationError


class AccountAccount(models.Model):
    _name = 'account.account'
    _inherit = ['account.account', 'mail.thread', 'ir.needaction_mixin']
    _order = 'id desc,state asc'
    _description = 'Chart of Account'

    name = fields.Char(size=50, track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    code = fields.Char(size=8, track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    parent_id = fields.Many2one(track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    user_type_id = fields.Many2one(track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    deprecated = fields.Boolean(track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    reconcile = fields.Boolean(track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    level_size = fields.Integer(related='level_id.size')

    level_id = fields.Many2one('account.account.level', ondelete='restrict', string='Level', required=True,
                               track_visibility='onchange')
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange', readonly=True,
                             states={'draft': [('readonly', False)]})
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approve'), ('reject', 'Reject')], default='draft',
                             track_visibility='onchange', )

    line_ids = fields.One2many('history.account.account', 'line_id', string='Lines', readonly=True,
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
                [('name', '=ilike', self.name.strip()), '|', ('active', '=', True), ('active', '=', False)])
            if len(name) > 1:
                raise Warning(_('[Unique Error] Name must be unique!'))

    @api.onchange("level_id")
    def onchange_levels(self):
        if self.level_id:
            res = {}
            self.parent_id = 0
            parents = self.search([('level_id', '=', self.level_id.parent_id.id)])
            res['domain'] = {
                'parent_id': [('id', 'in', parents.ids), ('internal_type', '=', 'view')],
            }
            return res

    @api.onchange("code")
    def onchange_strips(self):
        if self.code:
            filter = str(self.code.strip()).upper()
            if self.level_size == 1:
                code = filter[:self.level_size]
            else:
                code = self.parent_id.code + filter

            self.code = code[:self.level_id.size]

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
        if self.state == 'approve':
            self.state = 'draft'

    @api.one
    def act_approve(self):
        if self.state == 'draft':
            self.active = True
            self.pending = False
            self.state = 'approve'

    @api.one
    def act_reject(self):
        if self.state == 'draft':
            self.state = 'reject'
            self.pending = False

    @api.one
    def act_approve_pending(self):
        if self.pending == True:
            requested = self.line_ids.search([('state', '=', 'pending'), ('line_id', '=', self.id)],
                                             order='id desc',
                                             limit=1)
            if requested:
                self.name = requested.change_name
                self.active = requested.status
                self.pending = False
                requested.state = 'approve'
                requested.change_date = fields.Datetime.now()

    @api.one
    def act_reject_pending(self):
        if self.pending == True:
            requested = self.line_ids.search([('state', '=', 'pending'), ('line_id', '=', self.id)],
                                             order='id desc',
                                             limit=1)
            if requested:
                self.pending = False
                requested.state = 'reject'
                requested.change_date = fields.Datetime.now()

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'reject'):
                raise ValidationError(_('[Warning] Approve and Reject record cannot be deleted.'))

            try:
                return super(AccountAccount, rec).unlink()
            except IntegrityError:
                raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                        "- deletion: you may be trying to delete a record while other records still reference it"))


class HistoryAccountAccount(models.Model):
    _name = 'history.account.account'
    _description = 'History Account Account'
    _order = 'id desc'

    change_name = fields.Char('Proposed Name', size=50, readonly=True, states={'draft': [('readonly', False)]})
    status = fields.Boolean('Active', default=True, track_visibility='onchange')
    change_date = fields.Datetime(string='Date')
    line_id = fields.Many2one('account.account', ondelete='restrict')
    state = fields.Selection([('pending', 'Pending'), ('approve', 'Approve'), ('reject', 'Reject')],
                             default='pending')


class AccountAccountTag(models.Model):
    _inherit = 'account.account.tag'

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.search(
                [('name', '=ilike', self.name.strip()), '|', ('active', '=', True), ('active', '=', False)])
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
