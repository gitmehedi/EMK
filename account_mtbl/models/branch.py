from odoo import api, fields, models, _, SUPERUSER_ID
from psycopg2 import IntegrityError
from odoo.exceptions import ValidationError


class Branch(models.Model):
    _name = 'operating.unit'
    _order = 'code asc'
    _inherit = ['operating.unit', 'mail.thread']
    _description = 'Branch'

    name = fields.Char('Name', required=True, size=200, track_visibility='onchange', readonly=True,
                       states={'draft': [('readonly', False)]})
    code = fields.Char('Code', required=True, size=3, track_visibility='onchange', readonly=True,
                       states={'draft': [('readonly', False)]})
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange', readonly=True,
                             states={'draft': [('readonly', False)]})
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string='Status', track_visibility='onchange')
    company_id = fields.Many2one(
        'res.company', 'Company', required=True, track_visibility='onchange', default=lambda self:
        self.env['res.company']._company_default_get('account.account'), readonly=True,
        states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', 'Partner', required=True, default=lambda self:
    self.env['res.company']._company_default_get('account.account'), readonly=True,
                                 states={'draft': [('readonly', False)]})
    branch_type = fields.Selection([('metro', 'CHO'), ('urban', 'Urban'), ('rural', 'Rural')],
                                   string='Location of Branch', track_visibility='onchange', required=True,
                                   readonly=True,
                                   states={'draft': [('readonly', False)]})
    line_ids = fields.One2many('history.operating.unit', 'line_id', string='Lines', readonly=True,
                               states={'draft': [('readonly', False)]})
    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user.id, track_visibility='onchange')
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange')
    obu = fields.Boolean(default=False)
    currency_id = fields.Many2one('res.currency', string='Currency')


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
            if not self.code.isdigit():
                raise Warning(_('[Format Error] Code must be numeric!'))
            if len(self.code) != 3:
                raise Warning('[Format Error] Code must be 3 character!')

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
            requested = self.line_ids.search([('state', '=', 'pending'),
                                              ('line_id', '=', self.id)], order='id desc',limit=1)
            if requested:
                self.write({
                    'name': self.name if not requested.change_name else requested.change_name,
                    'pending': False,
                    'branch_type': requested.branch_type if requested.branch_type else self.branch_type,
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
        name = self.name
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
                return super(Branch, rec).unlink()
            except IntegrityError:
                raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                        "- deletion: you may be trying to delete a record while other records still reference it"))


class HistoryBranch(models.Model):
    _name = 'history.operating.unit'
    _description = 'History Branch'
    _order = 'id desc'

    change_name = fields.Char('Proposed Name', size=200, readonly=True, states={'draft': [('readonly', False)]})
    status = fields.Boolean('Active', default=True, track_visibility='onchange')
    request_date = fields.Datetime(string='Requested Date')
    change_date = fields.Datetime(string='Approved Date')
    branch_type = fields.Selection([('metro', 'CHO'), ('urban', 'Urban'), ('rural', 'Rural')],
                                   string='Location of Branch')
    line_id = fields.Many2one('operating.unit', ondelete='restrict')
    state = fields.Selection([('pending', 'Pending'), ('approve', 'Approved'), ('reject', 'Rejected')],
                             default='pending', string='Status')
