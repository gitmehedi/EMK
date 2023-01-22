from odoo import models, fields, api, _
from odoo.exceptions import Warning


class ResPartnerWizard(models.TransientModel):
    _name = 'res.partner.wizard'

    @api.model
    def default_name(self):
        context = self._context
        return self.env[context['active_model']].search([('id', '=', context['active_id'])]).name

    @api.model
    def default_status(self):
        context = self._context
        return self.env[context['active_model']].search([('id', '=', context['active_id'])]).active

    status = fields.Boolean(string='Active', default=default_status)
    name = fields.Char(string='Requested Name')
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
    parent_id = fields.Many2one('res.partner', 'Vendor Type')
    company_id = fields.Many2one('res.company', 'Company', index=True)
    entity_services = fields.Many2many('product.product', 'service_vendor_wizard_rel', 'service_id',
                                       'vendor_wizard_id', string='Service')
    designation_id = fields.Many2one('vendor.designation', string="Designation")
    contact_person = fields.Char(string='Contact Person')

    @api.onchange('company_type')
    def onchange_company_type(self):
        if self.company_type=='company':
            self.parent_id=None

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.env['res.partner'].search(
                [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                 ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.constrains('mobile')
    def _check_numeric_constrain(self):
        if self.mobile and not self.mobile.isdigit():
            raise Warning('[Format Error] Mobile must be numeric!')

    @api.constrains('tax', 'bin', 'tin', 'vat', 'mobile', 'fax', 'nid')
    def _check_numeric_constrain(self):
        if self.tax:
            tax = self.env['res.partner'].search(
                [('tax', '=ilike', self.tax.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                 ('active', '=', False)])
            if len(tax) > 1:
                raise Warning(_('[Unique Error] Trade License must be unique!'))
        if self.bin:
            bin = self.env['res.partner'].search(
                [('bin', '=ilike', self.bin.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                 ('active', '=', False)])
            if len(bin) > 1:
                raise Warning(_('[Unique Error] BIN Number must be unique!'))
            if len(self.bin) < 13:
                raise Warning('[Format Error] BIN must be at least 13 digit!')
        if self.vat:
            vat = self.env['res.partner'].search(
                [('vat', '=ilike', self.vat.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                 ('active', '=', False)])
            if len(vat) > 1:
                raise Warning(_('[Unique Error] VAT Registration must be unique!'))
            if len(self.vat) != 11 or not self.vat.isdigit():
                raise Warning('[Format Error] VAT Registration must be numeric with 11 digit!')
        if self.tin:
            tin = self.env['res.partner'].search(
                [('tin', '=ilike', self.tin.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                 ('active', '=', False)])
            if len(tin) > 1:
                raise Warning(_('[Unique Error] TIN Number must be unique!'))
            if len(self.tin) < 12:
                raise Warning('[Format Error] TIN must be at least 12 digit!')
        if self.mobile and not self.mobile.isdigit():
            raise Warning('[Format Error] Mobile must be numeric!')
        if self.fax and len(self.fax) != 16:
            raise Warning('[Format Error] Fax must be 16 character!')
        if self.nid:
            nid = self.env['res.partner'].search(
                [('nid', '=ilike', self.nid.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                 ('active', '=', False)])
            if len(nid) > 1:
                raise Warning(_('[Unique Error] NID must be unique!'))
            if len(self.nid) not in (17, 13, 10):
                raise Warning('[Format Error] NID must be 17/13/10 character!')
            if not self.nid.isdigit():
                raise Warning('[Format Error] NID must be numeric!')

    @api.multi
    def act_change_name(self):
        id = self._context['active_id']

        name = self.env['res.partner'].search([('name', '=ilike', self.name)])
        if len(name) > 0:
            raise Warning('[Unique Error] Name must be unique!')

        pending = self.env['history.res.partner'].search([('state', '=', 'pending'), ('line_id', '=', id)])
        if len(pending) > 0:
            raise Warning('[Warning] You already have a pending request!')
        company_type = fields.Selection(selection=[('person', 'Individual'), ('company', 'Company')],
                                        string='Company Type')
        parent_id = fields.Many2one('res.partner', 'Vendor Type')
        company_id = fields.Many2one('res.company', 'Company', index=True)
        self.env['history.res.partner'].create(
            {'change_name': self.name,
             'status': self.status,
             'website': self.website,
             'phone': self.phone,
             'mobile': self.mobile,
             'email': self.email,
             'street': self.street,
             'street2': self.street2,
             'country_id': self.country_id.id,
             'tax': self.tax,
             'vat': self.vat,
             'bin': self.bin,
             'tin': self.tin,
             'fax': self.fax,
             'nid': self.nid,
             'property_account_receivable_id': self.property_account_receivable_id.id,
             'property_account_payable_id': self.property_account_payable_id.id,
             'vendor_bank_acc': self.vendor_bank_acc,
             'division_id': self.division_id.id,
             'district_id': self.district_id.id,
             'upazila_id': self.upazila_id.id,
             'postal_code': self.postal_code.id,
             'designation_id': self.designation_id.id,
             'contact_person': self.contact_person,
             'company_type': self.company_type if self.company_type else None,
             'parent_id': self.parent_id.id if self.parent_id else None,
             'company_id': self.company_id.id if self.company_id else None,
             'entity_services': [(6, 0, self.entity_services.ids)],
             'request_date': fields.Datetime.now(),
             'line_id': id})
        record = self.env['res.partner'].search(
            [('id', '=', id), '|', ('active', '=', False), ('active', '=', True)])
        if record:
            record.write({'pending': True, 'maker_id': self.env.user.id})

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
