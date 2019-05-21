from odoo import api, fields, models, _
from psycopg2 import IntegrityError
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'mail.thread']

    name = fields.Char(track_visibility='onchange')
    parent_id = fields.Many2one(track_visibility='onchange')
    website = fields.Char(track_visibility='onchange')
    company_type = fields.Selection(track_visibility='onchange')
    category_id = fields.Many2many(track_visibility='onchange')
    function = fields.Char(track_visibility='onchange')
    tax = fields.Char(track_visibility='onchange')
    vat = fields.Char(track_visibility='onchange',size=11)
    bin = fields.Char(track_visibility='onchange',size=9)
    tin = fields.Char(track_visibility='onchange',size=12)
    title = fields.Many2one(track_visibility='onchange')
    lang = fields.Selection(track_visibility='onchange')
    customer = fields.Boolean(track_visibility='onchange')
    supplier = fields.Boolean(track_visibility='onchange')
    active = fields.Boolean(track_visibility='onchange')
    property_account_receivable_id = fields.Many2one(track_visibility='onchange',required=False)
    property_account_payable_id = fields.Many2one(track_visibility='onchange')
    email = fields.Char(track_visibility='onchange')
    phone = fields.Char(track_visibility='onchange')
    fax = fields.Char(track_visibility='onchange',size=16)
    mobile = fields.Char(track_visibility='onchange')
    street = fields.Char(track_visibility='onchange')
    street2 = fields.Char(track_visibility='onchange')
    zip = fields.Char(track_visibility='onchange')
    city = fields.Char(track_visibility='onchange')
    state_id = fields.Many2one(track_visibility='onchange')
    country_id = fields.Many2one(track_visibility='onchange',
                                 default=lambda self: self.env.user.company_id.country_id.id)
    company_id = fields.Many2one(track_visibility='onchange')

    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange', readonly=True,
                             states={'draft': [('readonly', False)]})
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approve'), ('reject', 'Reject')], default='draft',
                             track_visibility='onchange')

    line_ids = fields.One2many('history.res.partner', 'line_id', string='Lines', readonly=True,
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
                self.active = requested.status or False
                self.website = requested.website or False
                self.phone = requested.phone or False
                self.mobile = requested.mobile or False
                self.email = requested.email or False
                self.street = requested.street or False
                self.street2 = requested.street2 or False
                self.zip = requested.zip or False
                self.city = requested.city or False
                self.state_id = requested.state_id.id or False
                self.country_id = requested.country_id.id or False
                self.bank_ids = [i.id for i in requested.bank_ids] or False
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
                return super(ResPartner, rec).unlink()
            except IntegrityError:
                raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                        "- deletion: you may be trying to delete a record while other records still reference it"))

    @api.onchange("name")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()


    @api.constrains('tax','bin', 'tin','vat','mobile','fax')
    def _check_numeric_constrain(self):
        if self.tin:
            tax = self.search(
                [('tax', '=ilike', self.tax.strip()), '|', ('active', '=', True), ('active', '=', False)])
            if len(tax) > 1:
                raise Warning(_('[Unique Error] Trade License must be unique!'))
            if len(self.tin) != 12 or not self.tin.isdigit():
                raise Warning('[Format Error] TIN must be numeric with 12 digit!')
        if self.bin:
            bin = self.search(
                [('bin', '=ilike', self.bin.strip()), '|', ('active', '=', True), ('active', '=', False)])
            if len(bin) > 1:
                raise Warning(_('[Unique Error] BIN Number must be unique!'))
            if len(self.bin) != 9 or not self.bin.isdigit():
                raise Warning('[Format Error] BIN must be numeric with 9 digit!')
        if self.vat:
            vat = self.search(
                [('vat', '=ilike', self.vat.strip()), '|', ('active', '=', True), ('active', '=', False)])
            if len(vat) > 1:
                raise Warning(_('[Unique Error] VAT Registration must be unique!'))
            if len(self.vat) != 11 or not self.vat.isdigit():
                raise Warning('[Format Error] VAT Registration must be numeric with 11 digit!')
        if self.tin:
            tin = self.search(
                [('tin', '=ilike', self.tin.strip()), '|', ('active', '=', True), ('active', '=', False)])
            if len(tin) > 1:
                raise Warning(_('[Unique Error] TIN Number must be unique!'))
        if self.mobile and not self.mobile.isdigit():
            raise Warning('[Format Error] Mobile must be numeric!')
        if self.fax and len(self.fax) != 16:
            raise Warning('[Format Error] Fax must be 16 character!')


    """ All functions """
    @api.constrains('name')
    def _check_unique_name(self):
        if self.name:
            name = self.env['res.partner'].search([('name', '=ilike', self.name)])
            if self.supplier == True:
                if len(name) > 1:
                    raise ValidationError('[Unique Error] Vendor Name must be unique!')
            elif self.customer == True:
                if len(name) > 1:
                    raise ValidationError('[Unique Error] Customer Name must be unique!')
            else:
                if len(name) > 1:
                    raise ValidationError('[Unique Error] Name must be unique!')


class HistoryResPartner(models.Model):
    _name = 'history.res.partner'
    _description = 'History Partner'
    _order = 'id desc'

    change_name = fields.Char('Proposed Name', size=50, readonly=True, states={'draft': [('readonly', False)]})
    status = fields.Boolean('Active', default=True, track_visibility='onchange')
    request_date = fields.Datetime(string='Requested Date')
    change_date = fields.Datetime(string='Approved Date')
    website = fields.Char(string='Website')
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    email = fields.Char(string='Email')
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    bank_ids = fields.One2many('res.partner.bank', 'partner_id', string='Banks')
    line_id = fields.Many2one('res.partner', ondelete='restrict')
    state = fields.Selection([('pending', 'Pending'), ('approve', 'Approved'), ('reject', 'Rejected')],
                             default='pending')