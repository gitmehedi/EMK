from odoo import models, fields, api, _
from psycopg2 import IntegrityError
from odoo.exceptions import ValidationError


class AccountJournal(models.Model):
    _name = 'account.journal'
    _inherit = ['account.journal', 'mail.thread']
    _order = 'name desc'
    _description = 'Journal Type'


    name = fields.Char('Name', required=True, size=50, track_visibility='onchange', readonly=True,
                       states={'draft': [('readonly', False)]})
    code = fields.Char('Code', required=True, size=10, track_visibility='onchange', readonly=True,
                       states={'draft': [('readonly', False)]})
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange', readonly=True,
                             states={'draft': [('readonly', False)]})
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approve'), ('reject', 'Reject')], default='draft',
                             track_visibility='onchange')
    type = fields.Selection(track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one(track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    company_id = fields.Many2one(track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    operating_unit_id = fields.Many2one(string='Branch',track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    default_credit_account_id = fields.Many2one(track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    default_debit_account_id = fields.Many2one(track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    refund_sequence = fields.Boolean(track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    update_posted = fields.Boolean(track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    group_invoice_lines = fields.Boolean(track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    show_on_dashboard = fields.Boolean(track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    line_ids = fields.One2many('history.account.journal', 'line_id', string='Lines', readonly=True,
                               states={'draft': [('readonly', False)]})

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


    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'reject'):
                raise ValidationError(_('[Warning] Approves and Rejected record cannot be deleted.'))

            try:
                return super(AccountJournal, rec).unlink()
            except IntegrityError:
                raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                        "- deletion: you may be trying to delete a record while other records still reference it"))

class HistoryBranch(models.Model):
    _name = 'history.account.journal'
    _description = 'History Branch'
    _order = 'id desc'

    change_name = fields.Char('Proposed Name', size=50, readonly=True, states={'draft': [('readonly', False)]})
    status = fields.Boolean('Active', default=True, track_visibility='onchange')
    change_date = fields.Datetime(string='Date')
    line_id = fields.Many2one('account.journal', ondelete='restrict')
    state = fields.Selection([('pending', 'Pending'), ('approve', 'Approve'), ('reject', 'Reject')],
                             default='pending')
