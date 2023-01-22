from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
from psycopg2 import IntegrityError


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'mail.thread']

    name = fields.Char(string='Name',track_visibility='onchange')
    parent_id = fields.Many2one(track_visibility='onchange')
    website = fields.Char(track_visibility='onchange')
    company_type = fields.Selection(track_visibility='onchange', store=True)
    category_id = fields.Many2many(track_visibility='onchange')
    function = fields.Char(track_visibility='onchange')

    tax = fields.Char(string='Trade License', track_visibility='onchange')
    vat = fields.Char(string='VAT Registration', track_visibility='onchange',size=11)
    bin = fields.Char(string='BIN Number', track_visibility='onchange',size=19)
    tin = fields.Char(string='TIN Number', track_visibility='onchange',size=16)

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
    street = fields.Char(string='Street',track_visibility='onchange')
    street2 = fields.Char(string='ETC',track_visibility='onchange')
    zip = fields.Char(track_visibility='onchange')
    city = fields.Char(string='City',track_visibility='onchange')
    state_id = fields.Many2one(track_visibility='onchange')
    country_id = fields.Many2one(track_visibility='onchange',
                                 default=lambda self: self.env.user.company_id.country_id.id)
    company_id = fields.Many2one(track_visibility='onchange')

    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange', readonly=True,
                             states={'draft': [('readonly', False)]})
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
                             string="Status",track_visibility='onchange')

    line_ids = fields.One2many('history.res.partner', 'line_id', string='Lines', readonly=True,
                               states={'draft': [('readonly', False)]})

    vendor_bank_acc = fields.Char('Vendor Bank Account',readonly=True,size=13,
                                  states={'draft': [('readonly', False)]},
                                  help="This is the Account number which using "
                                       "for payments against vendor.")
    nid = fields.Char('NID',size=17,readonly=True,states={'draft': [('readonly', False)]},
                      help="NID which is 17/13/10 digit.",track_visibility='onchange')
    division_id = fields.Many2one('bd.division',string='Division',readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  track_visibility='onchange')
    district_id = fields.Many2one('bd.district', string='District', readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  track_visibility='onchange')
    upazila_id = fields.Many2one('bd.upazila', string='Upazila/Thana', readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 track_visibility='onchange')
    postal_code = fields.Many2one('bd.postal.code','Postal Code',readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  track_visibility='onchange')
    entity_services = fields.Many2many('product.product', 'service_vendor_rel','service_id','vendor_id',
                                       string='Service', readonly=True,
                                       states={'draft': [('readonly', False)]},
                                       track_visibility='onchange')
    designation_id = fields.Many2one('vendor.designation', string="Designation")
    contact_person = fields.Char(string='Contact Person')
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
                self.name = self.name if not requested.change_name else requested.change_name
                self.active = self.active if not requested.status else requested.status
                self.website = self.website if not requested.website else requested.website
                self.phone = self.phone if not requested.phone else requested.phone
                self.mobile = self.mobile if not requested.mobile else requested.mobile
                self.email = self.email if not requested.email else requested.email
                self.street = self.street if not requested.street else requested.street
                self.street2 = self.street2 if not requested.street2 else requested.street2
                self.country_id = self.country_id if not requested.country_id.id else requested.country_id.id

                self.tax = self.tax if not requested.tax else requested.tax
                self.vat = self.vat if not requested.vat else requested.vat
                self.bin = self.bin if not requested.bin else requested.bin
                self.tin = self.tin if not requested.tin else requested.tin
                self.fax = self.fax if not requested.fax else requested.fax
                self.nid = self.nid if not requested.nid else requested.nid
                self.property_account_receivable_id = self.property_account_receivable_id if not \
                    requested.property_account_receivable_id.id else requested.property_account_receivable_id.id
                self.property_account_payable_id = self.property_account_payable_id if not \
                    requested.property_account_payable_id.id else requested.property_account_payable_id.id
                self.vendor_bank_acc = self.vendor_bank_acc if not requested.vendor_bank_acc else \
                    requested.vendor_bank_acc
                self.division_id = self.division_id if not requested.division_id.id else requested.division_id.id
                self.district_id = self.district_id if not requested.district_id.id else requested.district_id.id
                self.upazila_id = self.upazila_id if not requested.upazila_id.id else requested.upazila_id.id
                self.postal_code = self.postal_code if not requested.postal_code.id else requested.postal_code.id
                self.contact_person = self.contact_person if not requested.contact_person else requested.contact_person
                self.company_type = self.company_type if not requested.company_type else requested.company_type
                self.parent_id = self.parent_id if not requested.parent_id else requested.parent_id
                self.company_id = self.company_id if not requested.company_id else requested.company_id
                self.designation_id = self.designation_id if not requested.designation_id.id else \
                    requested.designation_id.id
                if requested.entity_services:
                    self.entity_services = [(6, 0, requested.entity_services.ids)]

                self.pending = False
                self.approver_id = self.env.user.id
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

    @api.onchange("division_id")
    def onchange_division(self):
        if self.division_id:
            self.district_id = []
            self.upazila_id = []
            return {
                'domain': {'district_id': [('division_id', '=', self.division_id.id)],
                           'upazila_id': [('division_id', '=', self.division_id.id)]
                           }
            }

    @api.onchange("district_id")
    def onchange_district(self):
        if self.district_id:
            self.upazila_id = []
            return {
                'domain': {'upazila_id': [('district_id', '=', self.district_id.id)]
                           }
            }

    @api.onchange("upazila_id")
    def onchange_upazila(self):
        if self.upazila_id:
            self.postal_code = []
            return {
                'domain': {'postal_code': [('upazila_id', '=', self.upazila_id.id)]
                           }
            }


    @api.constrains('tax', 'bin', 'tin', 'vat', 'mobile', 'fax')
    def _check_numeric_constrain(self):
        for partner in self:
            if partner.tax:
                tax = self.search(
                    [('tax', '=ilike', partner.tax.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                     ('active', '=', False)])
                if len(tax) > 1:
                    raise Warning(_('[Unique Error] Trade License must be unique!'))
            if partner.bin:
                bin = self.search(
                    [('bin', '=ilike', partner.bin.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                     ('active', '=', False)])
                if len(bin) > 1:
                    raise Warning(_('[Unique Error] BIN Number must be unique!'))
                if len(partner.bin) < 13:
                    raise Warning('[Format Error] BIN must be at least 13 digit!')
            if partner.vat:
                vat = self.search(
                    [('vat', '=ilike', partner.vat.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                     ('active', '=', False)])
                if len(vat) > 1:
                    raise Warning(_('[Unique Error] VAT Registration must be unique!'))
                if len(partner.vat) != 11 or not partner.vat.isdigit():
                    raise Warning('[Format Error] VAT Registration must be numeric with 11 digit!')
            if partner.tin:
                tin = self.search(
                    [('tin', '=ilike', partner.tin.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                     ('active', '=', False)])
                if len(tin) > 1:
                    raise Warning(_('[Unique Error] TIN Number must be unique!'))
                if len(partner.tin) < 12:
                    raise Warning('[Format Error] TIN must be at least 12 digit!')
            if partner.mobile and not partner.mobile.isdigit():
                raise Warning('[Format Error] Mobile must be numeric!')
            if partner.fax and len(partner.fax) != 16:
                raise Warning('[Format Error] Fax must be 16 character!')

    @api.constrains('nid')
    def _check_nid_constrain(self):
        if self.nid:
            nid = self.search(
                [('nid', '=ilike', self.nid.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True), ('active', '=', False)])
            if len(nid) > 1:
                raise Warning(_('[Unique Error] NID must be unique!'))
            if len(self.nid) not in (17,13,10):
                raise Warning('[Format Error] NID must be 17/13/10 character!')
            if not self.nid.isdigit():
                raise Warning('[Format Error] NID must be numeric!')

class HistoryResPartner(models.Model):
    _name = 'history.res.partner'
    _description = 'History Partner'
    _order = 'id desc'

    change_name = fields.Char('Proposed Name', size=200, readonly=True, states={'draft': [('readonly', False)]})
    status = fields.Boolean('Active', default=True, track_visibility='onchange')
    request_date = fields.Datetime(string='Requested Date')
    change_date = fields.Datetime(string='Approved Date')
    line_id = fields.Many2one('res.partner', ondelete='restrict')
    state = fields.Selection([('pending', 'Pending'), ('approve', 'Approved'), ('reject', 'Rejected')],
                             default='pending')
    website = fields.Char(string='Website')
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    email = fields.Char(string='Email')
    street = fields.Char(string='Street')
    street2 = fields.Char(string='ETC')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict',
                                 default=lambda self: self.env.user.company_id.country_id.id)
    tax = fields.Char(string='Trade License')
    vat = fields.Char(string='VAT Registration', size=11)
    bin = fields.Char(string='BIN Number', size=19)
    tin = fields.Char(string='TIN Number', size=16)
    fax = fields.Char(string='Fax', size=16)
    nid = fields.Char(string='NID', size=17)
    property_account_receivable_id = fields.Many2one('account.account', string='Account Receivable',
                                                     domain="[('internal_type', '=', 'receivable')]")
    property_account_payable_id = fields.Many2one('account.account', string='Account Payable',
                                                  domain="[('internal_type', '=', 'payable')]")
    vendor_bank_acc = fields.Char(string='Vendor Bank Account',size=13)
    division_id = fields.Many2one('bd.division', string='Division')
    district_id = fields.Many2one('bd.district', string='District')
    upazila_id = fields.Many2one('bd.upazila', string='Upazila/Thana')
    postal_code = fields.Many2one('bd.postal.code', 'Postal Code')
    company_type = fields.Selection(selection=[('person', 'Individual'), ('company', 'Company')], string='Company Type')
    parent_id = fields.Many2one('res.partner', 'Company')
    company_id = fields.Many2one('res.company', 'Company', index=True)
    entity_services = fields.Many2many('product.product', 'service_vendor_history_rel', 'service_id',
                                       'vendor_history_id', string='Service')
    designation_id = fields.Many2one('vendor.designation', string="Designation")
    contact_person = fields.Char(string='Contact Person')


class InheritResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def create(self, vals):
        user = super(InheritResUsers, self).create(vals)
        if user.partner_id:
            user.partner_id.write({
                'email': user.login + "@mtb.com"
            })
        return user
