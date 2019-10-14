from odoo import api, fields, models, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class DateRangeType(models.Model):
    _name = "date.range.type"
    _order = 'name desc'
    _inherit = ['date.range.type', 'mail.thread']
    _description = 'Account Period Type'

    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('date.range.type')

    name = fields.Char('Name', required=True, size=200, track_visibility='onchange', readonly=True,
                       states={'draft': [('readonly', False)]}, translate=True)
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange', readonly=True,
                             states={'draft': [('readonly', False)]})
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status',track_visibility='onchange')
    allow_overlap = fields.Boolean(string="Allow Overlap", readonly=True,
                                   states={'draft': [('readonly', False)]})
    fiscal_year = fields.Boolean(string='Is Fiscal Year?', readonly=True,
                                 states={'draft': [('readonly', False)]})
    fiscal_month = fields.Boolean(string="Is Fiscal Month?", readonly=True,
                                  states={'draft': [('readonly', False)]})
    tds_year = fields.Boolean(string="Is TDS Year?", default=False, readonly=True,
                              states={'draft': [('readonly', False)]})
    parent_type_id = fields.Many2one(string="Parent Type", readonly=True,
                                     states={'draft': [('readonly', False)]})
    line_ids = fields.One2many('history.date.range.type', 'line_id', string='Lines', readonly=True,
                               states={'draft': [('readonly', False)]})
    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user.id, track_visibility='onchange')
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange')

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.search(
                [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True), ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.onchange("name", )
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
                self.write({
                    'name': self.name if not requested.change_name else requested.change_name,
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

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'reject'):
                raise ValidationError(_('[Warning] Approves and Rejected record cannot be deleted.'))

            try:
                return super(DateRangeType, rec).unlink()
            except DateRangeType:
                raise ValidationError(
                    _("The operation cannot be completed, probably due to the following:\n"
                      "- deletion: you may be trying to delete a record while other records still reference it"))


class HistoryAccountPeriodType(models.Model):
    _name = 'history.date.range.type'
    _description = 'History Account Period Type'
    _order = 'id desc'

    change_name = fields.Char('Proposed Name', size=200, readonly=True, states={'draft': [('readonly', False)]})
    status = fields.Boolean('Active', default=True, track_visibility='onchange')
    request_date = fields.Datetime(string='Requested Date')
    change_date = fields.Datetime(string='Approved Date')
    line_id = fields.Many2one('date.range.type', ondelete='restrict')
    state = fields.Selection([('pending', 'Pending'), ('approve', 'Approved'), ('reject', 'Rejected')],
                             default='pending',string='Status')
