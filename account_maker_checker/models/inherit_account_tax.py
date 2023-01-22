from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import Warning, ValidationError
from psycopg2 import IntegrityError


class AccountTax(models.Model):
    _name = 'account.tax'
    _inherit = ['account.tax', 'mail.thread', 'ir.needaction_mixin']

    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user.id, track_visibility='onchange')
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange')
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange', readonly=True,
                             states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             track_visibility='onchange', string='Status')
    history_ids = fields.One2many('history.account.tax', 'history_id', string='Lines', readonly=True,
                               states={'draft': [('readonly', False)]})
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})

    @api.one
    def act_approve(self):
        if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
            raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))
        if self.state == 'draft':
            self.write({
                'state': 'approve',
                'pending': False,
                'active': True,
                'approver_id': self.env.user.id
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
    def act_reject_pending(self):
        if self.pending == True:
            requested = self.history_ids.search([('state', '=', 'pending'), ('history_id', '=', self.id)],
                                                order='id desc', limit=1)
            if requested:
                self.write({
                    'pending': False
                })
                requested.write({
                    'state': 'reject',
                    'change_date': fields.Datetime.now()
                })

    @api.one
    def act_approve_pending(self):
        if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
            raise ValidationError(_("[Validation Error] Editor and Approver can't be same person!"))
        if self.pending == True:
            requested = self.history_ids.search([('state', '=', 'pending'), ('history_id', '=', self.id)],
                                                order='id desc', limit=1)
            if requested:
                self.write({
                    'name': self.name if not requested.change_name else requested.change_name,
                    'pending': False,
                    'active': requested.status,
                    'approver_id': self.env.user.id
                })
                requested.write({
                    'state': 'approve',
                    'change_date': fields.Datetime.now()
                })

    @api.one
    def act_draft(self):
        if self.state == 'reject':
            self.write({
                'state': 'draft',
                'pending': True,
                'active': False,
            })

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            if self.is_vat:
                name = self.search(
                    [('name', '=ilike', self.name.strip()), ('is_vat', '=', True), ('state', '!=', 'reject'),
                     '|', ('active', '=', True), ('active', '=', False)])
            elif self.is_tds:
                name = self.search(
                    [('name', '=ilike', self.name.strip()), ('is_tds', '=', True), ('state', '!=', 'reject'),
                     '|', ('active', '=', True), ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'reject'):
                raise ValidationError(_('[Warning] Approves and Rejected record cannot be deleted.'))

            try:
                return super(AccountTax, rec).unlink()
            except IntegrityError:
                raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                        "- deletion: you may be trying to delete a record while"
                                        " other records still reference it"))

class HistoryVAT(models.Model):
    _name = 'history.account.tax'
    _description = 'VAT/TDS Rule Changing History'
    _order = 'id desc'

    change_name = fields.Char('Proposed Name', size=200, readonly=True, states={'draft': [('readonly', False)]})
    status = fields.Boolean('Active', default=True, track_visibility='onchange')
    request_date = fields.Datetime(string='Requested Date')
    change_date = fields.Datetime(string='Approved Date')
    history_id = fields.Many2one('account.tax', ondelete='restrict')
    state = fields.Selection([('pending', 'Pending'), ('approve', 'Approved'), ('reject', 'Rejected')],
                             default='pending')