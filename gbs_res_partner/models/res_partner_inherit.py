from odoo import api, fields, models, _
from psycopg2 import IntegrityError
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'mail.thread']

    name = fields.Char(string='Name',track_visibility='onchange')
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

    vendor_bank_acc = fields.Char('Vendor Bank Account',readonly=True,
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
    entity_services = fields.Many2many('entity.service', 'service_partner_rel','service_id','partner_id',
                                       string='Service', readonly=True,
                                       states={'draft': [('readonly', False)]},
                                       track_visibility='onchange')

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
                self.name = self.name if not requested.change_name else requested.change_name
                self.active = self.status if not requested.status else requested.status
                self.website = self.website if not requested.website else requested.website
                self.phone = self.phone if not requested.phone else requested.phone
                self.mobile = self.mobile if not requested.mobile else requested.mobile
                self.email = self.email if not requested.email else requested.email
                self.street =  self.street if not requested.street else requested.street
                self.street2 =  self.street2 if not requested.street2 else requested.street2
                self.zip =  self.zip if not requested.zip else requested.zip
                self.city = self.city if not requested.city else requested.city
                self.state_id = self.state_id if not requested.state_id.id else requested.state_id.id
                self.country_id = self.country_id if not requested.country_id.id else requested.country_id.id
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


    @api.constrains('tax','bin', 'tin','vat','mobile','fax')
    def _check_numeric_constrain(self):
        if self.tax:
            tax = self.search(
                [('tax', '=ilike', self.tax.strip()), '|', ('active', '=', True), ('active', '=', False)])
            if len(tax) > 1:
                raise Warning(_('[Unique Error] Trade License must be unique!'))
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
            if len(self.tin) != 12 or not self.tin.isdigit():
                raise Warning('[Format Error] TIN must be numeric with 12 digit!')
        if self.mobile and not self.mobile.isdigit():
            raise Warning('[Format Error] Mobile must be numeric!')
        if self.fax and len(self.fax) != 16:
            raise Warning('[Format Error] Fax must be 16 character!')

    @api.constrains('nid')
    def _check_nid_constrain(self):
        if self.nid:
            nid = self.search(
                [('nid', '=ilike', self.nid.strip()), '|', ('active', '=', True), ('active', '=', False)])
            if len(nid) > 1:
                raise Warning(_('[Unique Error] NID must be unique!'))
            if len(self.nid) not in (17,13,10):
                raise Warning('[Format Error] NID must be 17/13/10 character!')
            if not self.nid.isdigit():
                raise Warning('[Format Error] NID must be numeric!')

    # @api.constrains('postal_code')
    # def _check_postal_code_constrain(self):
    #     if self.postal_code:
    #         if len(self.postal_code) != 4:
    #             raise Warning('[Format Error] Postal Code  must be 4 digit!')
    #         if not self.postal_code.isdigit():
    #             raise Warning('[Format Error] Postal Code must be numeric!')

    @api.multi
    def _display_address(self, without_company=False):
        """
        Inject a context key to prevent the 'street' name to be
        deleted from the result of _address_fields when called from
        the super.
        """
        res = super(ResPartner,self).display_address(without_company=without_company)
        return res


    """ All functions """
    @api.constrains('name')
    def _check_unique_name(self):
        if self.name:
            name = self.env['res.partner'].search([('name', '=ilike', self.name),'|',('active', '=', True), ('active', '=', False)])
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

    change_name = fields.Char('Proposed Name', size=200, readonly=True, states={'draft': [('readonly', False)]})
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
    line_id = fields.Many2one('res.partner', ondelete='restrict')
    state = fields.Selection([('pending', 'Pending'), ('approve', 'Approved'), ('reject', 'Rejected')],
                             default='pending')