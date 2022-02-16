# -*- coding: utf-8 -*-
from psycopg2 import IntegrityError

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import Warning, ValidationError


class AccountAnalyticAccount(models.Model):
    _name = 'account.analytic.account'
    _inherit = ['account.analytic.account', 'mail.thread', 'ir.needaction_mixin']
    _order = 'code asc,state asc'
    _description = 'Cost Centre'

    name = fields.Char('Name', required=True, size=200, track_visibility='onchange', readonly=True,
                       states={'draft': [('readonly', False)]})
    code = fields.Char('Code', required=True, size=3, track_visibility='onchange', readonly=True,
                       states={'draft': [('readonly', False)]})
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange', readonly=True,
                             states={'draft': [('readonly', False)]})
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    operating_unit_ids = fields.Many2many(string='Branch', track_visibility='onchange',
                                          readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status', track_visibility='onchange', )
    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user.id, track_visibility='onchange')

    @api.constrains('name', 'code')
    def _check_unique_constrain(self):
        if self.name or self.code:
            name = self.search(
                [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                 ('active', '=', False)])
            code = self.search(
                [('code', '=ilike', self.code.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                 ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')
            if len(code) > 1:
                raise Warning('[Unique Error] Code must be unique!')
            if len(self.code) != 3 or not self.code.isdigit():
                raise Warning(_('[Format Error] Code must be numeric with 3 digit!'))

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'draft')]

    @api.one
    def name_get(self):
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

    @api.onchange("name", "code")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()
        if self.code:
            self.code = str(self.code.strip()).upper()

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
                'active': True
            })

    @api.one
    def act_reject(self):
        if self.state == 'draft':
            self.write({
                'state': 'reject',
                'pending': False,
                'active': False,
            })

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'reject'):
                raise ValidationError(_(Message.UNLINK_WARNING))

            try:
                return super(AccountAnalyticAccount, rec).unlink()
            except IntegrityError:
                raise ValidationError(_(Message.UNLINK_INT_WARNING))

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    _order = 'id desc'
    _description = 'Cost Centre Line'

    name = fields.Char(required=True, size=200, track_visibility='onchange')

    @api.one
    def name_get(self):
        name = self.name
        if self.name:
            name = '%s' % (self.name)
        return (self.id, name)

    @api.onchange("name")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()
