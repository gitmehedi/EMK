from odoo import models, fields, api, _, SUPERUSER_ID
from psycopg2 import IntegrityError
from odoo.exceptions import ValidationError


class AccountJournal(models.Model):
    _name = 'account.journal'
    _inherit = ['account.journal', 'mail.thread']
    _order = 'name desc'
    _description = 'Journal Type'

    name = fields.Char('Name', required=True, size=200, track_visibility='onchange', readonly=True,
                       states={'draft': [('readonly', False)]})
    code = fields.Char('Code', required=True, size=10, track_visibility='onchange', readonly=True,
                       states={'draft': [('readonly', False)]})
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange', readonly=True,
                             states={'draft': [('readonly', False)]})
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status', track_visibility='onchange')
    type = fields.Selection(track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one(track_visibility='onchange', readonly=True,
                                  states={'draft': [('readonly', False)]})
    company_id = fields.Many2one(track_visibility='onchange', readonly=True,
                                 states={'draft': [('readonly', False)]})
    operating_unit_id = fields.Many2one(string='Branch', track_visibility='onchange', readonly=True,
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
    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user.id, track_visibility='onchange')
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange')

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
                self.write({
                    'name': self.name if not requested.change_name else requested.change_name,
                    'default_debit_account_id': self.default_debit_account_id.id if not requested.default_debit_account_id else requested.default_debit_account_id.id,
                    'default_credit_account_id': self.default_credit_account_id.id if not requested.default_credit_account_id else requested.default_credit_account_id.id,
                    'pending': False,
                    'active': requested.status,
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


class HistoryAccountJournal(models.Model):
    _name = 'history.account.journal'
    _description = 'History Account Journal'
    _order = 'id desc'

    change_name = fields.Char('Proposed Name', size=200, readonly=True, states={'draft': [('readonly', False)]})
    status = fields.Boolean('Active', default=True, track_visibility='onchange')
    request_date = fields.Datetime(string='Requested Date')
    change_date = fields.Datetime(string='Approved Date')
    line_id = fields.Many2one('account.journal', ondelete='restrict')
    default_debit_account_id = fields.Many2one('account.account', string='Debit Account',
                                               help='Default Debit Account of the Payment')
    default_credit_account_id = fields.Many2one('account.account', string='Credit Account',
                                                help='Default Credit Account of the Payment')
    state = fields.Selection([('pending', 'Pending'), ('approve', 'Approved'), ('reject', 'Rejected')],
                             default='pending', string='Status')
