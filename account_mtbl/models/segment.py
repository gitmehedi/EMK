# -*- coding: utf-8 -*-
from psycopg2 import IntegrityError

from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError


class Segment(models.Model):
    _name = 'segment'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc,state asc'
    _description = 'Segment'

    name = fields.Char('Name', required=True, size=50, track_visibility='onchange', readonly=True,
                       states={'draft': [('readonly', False)]})
    code = fields.Char('Code', required=True, size=1, track_visibility='onchange', readonly=True,
                       states={'draft': [('readonly', False)]})
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange', readonly=True,
                             states={'draft': [('readonly', False)]})
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approve'), ('reject', 'Reject')], default='draft',
                             track_visibility='onchange')
    line_ids = fields.One2many('history.segment', 'line_id', string='Lines', readonly=True,
                               states={'draft': [('readonly', False)]})

    @api.constrains('name', 'code')
    def _check_unique_constrain(self):
        if self.name or self.code:
            name = self.search(
                [('name', '=ilike', self.name.strip()), '|', ('active', '=', True), ('active', '=', False)])
            code = self.search(
                [('code', '=ilike', self.code.strip()), '|', ('active', '=', True), ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')
            if len(code) > 1:
                raise Warning('[Unique Error] Code must be unique!')
            if len(self.code) != 1 or not self.code.isdigit():
                raise Warning(_('[Format Error] Code must be numeric with 1 digit!'))

    @api.onchange("name", "code")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()
        if self.code:
            self.code = str(self.code.strip()).upper()

    @api.one
    def name_get(self):
        name = self.name
        if self.name and self.code:
            name = '[%s] %s' % (self.code, self.name)
        return (self.id, name)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        names1 = super(models.Model, self).name_search(name=name, args=args, operator=operator, limit=limit)
        names2 = []
        if name:
            domain = [('code', '=ilike', name + '%')]
            names2 = self.search(domain, limit=limit).name_get()
        return list(set(names1) | set(names2))[:limit]

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'draft'), ('pending', '=', True)]

    @api.one
    def name_get(self):
        if self.name and self.code:
            name = '[%s] %s' % (self.code, self.name)
        return (self.id, name)

    @api.onchange("name", "code")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()
        if self.code:
            self.code = str(self.code.strip()).upper()

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
            self.active = False

    @api.one
    def act_approve_pending(self):
        if self.pending == True:
            requested = self.line_ids.search([('state', '=', 'pending'), ('line_id', '=', self.id)], order='id desc',
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
            requested = self.line_ids.search([('state', '=', 'pending'), ('line_id', '=', self.id)], order='id desc',
                                             limit=1)
            if requested:
                self.pending = False
                requested.state = 'reject'
                requested.change_date = fields.Datetime.now()

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'reject'):
                raise ValidationError(_('[Warning] Approves and Rejected record cannot be deleted.'))

            try:
                return super(Segment, rec).unlink()
            except IntegrityError:
                raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                        "- deletion: you may be trying to delete a record while other records still reference it"))


class HistorySegment(models.Model):
    _name = 'history.segment'
    _description = 'History Segmen'
    _order = 'id desc'

    change_name = fields.Char('Proposed Name', size=50, readonly=True, states={'draft': [('readonly', False)]})
    status = fields.Boolean('Active', default=True, track_visibility='onchange')
    change_date = fields.Datetime(string='Date')
    line_id = fields.Many2one('segment', ondelete='restrict')
    state = fields.Selection([('pending', 'Pending'), ('approve', 'Approve'), ('reject', 'Reject')],
                             default='pending')
