# -*- coding: utf-8 -*-
from psycopg2 import IntegrityError

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import Warning, ValidationError


class SubOperatingUnit(models.Model):
    _name = 'sub.operating.unit'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'account_id asc,code asc'
    _description = 'Sequence'

    name = fields.Char('Name', required=True, size=200, track_visibility='onchange', readonly=True,
                       states={'draft': [('readonly', False)]})
    code = fields.Char('Sequence', required=True, size=3, track_visibility='onchange', readonly=True,
                       states={'draft': [('readonly', False)]})
    account_id = fields.Many2one('account.account', string='CGL Account', readonly=True,
                                 states={'draft': [('readonly', False)]}, required=True)
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange', readonly=True,
                             states={'draft': [('readonly', False)]})
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             track_visibility='onchange', string='Status')

    line_ids = fields.One2many('history.sub.operating.unit', 'line_id', string='Lines', readonly=True,
                               states={'draft': [('readonly', False)]})
    all_branch = fields.Boolean(string='All Branch', default=True, track_visibility='onchange', readonly=True,
                                states={'draft': [('readonly', False)]})
    branch_ids = fields.Many2many('operating.unit', 'sequence_branch_rel', 'sequence_id', 'branch_id',
                                  string='Allowed Branches', track_visibility='onchange', readonly=True,
                                  states={'draft': [('readonly', False)]})
    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user.id, track_visibility='onchange')
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange')

    @api.constrains('account_id.code', 'code')
    def _check_unique_constrain(self):
        if self.name or self.code:
            name = self.search([('account_id.code', '=ilike', self.account_id.code.strip()), ('state', '!=', 'reject'),
                                ('code', '=', self.code.strip()), '|',
                                ('active', '=', True), ('active', '=', False)])
            if len(name) > 1:
                raise Warning(_('[Unique Error] Combination of GL Account and Code must be unique!'))

            if len(self.code) != 3 or not self.code.isdigit():
                raise Warning(_('[Format Error] Code must be numeric with 3 digit!'))

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'draft')]

    @api.one
    def name_get(self):
        name = self.name
        if self.name and self.code and self.account_id.code:
            name = '%s-%s-%s' % (self.account_id.code, self.code, self.name)
        return (self.id, name)

    @api.model
    def name_search(self, name, args=None, operator='=ilike', limit=100):
        names1 = super(models.Model, self).name_search(name=name, args=args, operator=operator, limit=limit)
        names2 = []
        if name:
            domain = ['|', '|', ('code', '=ilike', name + '%'), ('name', '=ilike', name + '%'),
                      ('account_id.code', '=ilike', name + '%')]
            names2 = self.search(domain, limit=limit, order='code ASC').name_get()

        return list(set(names1) | set(names2))[:limit]

    @api.onchange("name", "code")
    def onchange_strips(self):
        if self.name:
            self.name = str(self.name.strip()).upper()
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
            inc = [(4, rec.id) for rec in requested.inc_branch_ids]
            excl = [(3, val.id) for val in requested.excl_branch_ids]
            if requested:
                if requested.all_branch:
                    self.write({
                        'name': self.name if not requested.change_name else requested.change_name,
                        'pending': False,
                        'active': requested.status,
                        'branch_ids': [],
                        'all_branch': requested.all_branch,
                        'approver_id': self.env.user.id,
                    })
                else:
                    self.write({
                        'name': self.name if not requested.change_name else requested.change_name,
                        'pending': False,
                        'active': requested.status,
                        'branch_ids': inc + excl,
                        'all_branch': requested.all_branch,
                        'approver_id': self.env.user.id,
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
                return super(SubOperatingUnit, rec).unlink()
            except IntegrityError:
                raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                        "- deletion: you may be trying to delete a record while other records still reference it"))


class HistorySubOperatingUnit(models.Model):
    _name = 'history.sub.operating.unit'
    _description = 'History Sequence'
    _order = 'id desc'

    change_name = fields.Char('Proposed Name', size=200, readonly=True, states={'draft': [('readonly', False)]})
    status = fields.Boolean('Active', default=True, track_visibility='onchange')
    excl_branch_ids = fields.Many2many('operating.unit', 'history_seq_branch_excl_rel', string='Exclude Branch')
    inc_branch_ids = fields.Many2many('operating.unit', 'history_seq_branch_inc_rel', string='Include Branch')
    all_branch = fields.Boolean(string='All Branch', default=True)
    request_date = fields.Datetime(string='Requested Date')
    change_date = fields.Datetime(string='Approved Date')
    line_id = fields.Many2one('sub.operating.unit', ondelete='restrict')
    state = fields.Selection([('pending', 'Pending'), ('approve', 'Approved'), ('reject', 'Rejected')],
                             default='pending', string='Status')
