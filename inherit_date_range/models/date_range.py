from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class DateRange(models.Model):
    _name = "date.range"
    _order = 'name desc'
    _inherit = ['date.range', 'mail.thread']
    _description = 'Account Period'

    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('date.range')

    name = fields.Char('Name', required=True, size=50, track_visibility='onchange', readonly=True,
                       states={'draft': [('readonly', False)]}, translate=True)
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange', readonly=True,
                             states={'draft': [('readonly', False)]})
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approve'), ('reject', 'Reject')], default='draft',
                             track_visibility='onchange')
    date_start = fields.Date(string='Start Date', required=True, readonly=True,
                             states={'draft': [('readonly', False)]})
    date_end = fields.Date(string='End Date', required=True, readonly=True,
                           states={'draft': [('readonly', False)]})
    line_ids = fields.One2many('history.date.range', 'line_id', string='Lines', readonly=True,
                               states={'draft': [('readonly', False)]})

    @api.one
    def act_draft(self):
        if self.state == 'approve':
            self.write({
                'state': 'draft'
            })

    @api.one
    def act_approve(self):
        if self.state == 'draft':
            self.write({
                'state': 'approve',
                'pending': False,
                'active': True,
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
                return super(DateRange, rec).unlink()
            except DateRange:
                raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                        "- deletion: you may be trying to delete a record while other records still reference it"))

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.search(
                [('name', '=ilike', self.name.strip()), '|', ('active', '=', True), ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.onchange("name", )
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()

    @api.one
    def name_get(self):
        name = self.name
        if self.name and self.date_start and self.date_end:
            name = '[%s - %s] %s' % (self.date_start, self.date_end, self.name)
        return (self.id, name)


class HistoryAccountPeriod(models.Model):
    _name = 'history.date.range'
    _description = 'History Account Period'
    _order = 'id desc'

    change_name = fields.Char('Proposed Name', size=50, readonly=True, states={'draft': [('readonly', False)]})
    status = fields.Boolean('Active', default=True, track_visibility='onchange')
    request_date = fields.Datetime(string='Requested Date')
    change_date = fields.Datetime(string='Approved Date')
    line_id = fields.Many2one('sub.operating.unit', ondelete='restrict')
    state = fields.Selection([('pending', 'Pending'), ('approve', 'Approved'), ('reject', 'Rejected')],
                             default='pending')

