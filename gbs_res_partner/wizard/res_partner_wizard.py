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
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict',default=lambda self: self.env.user.company_id.country_id.id)
    tax = fields.Char(string='Trade License')
    vat = fields.Char(string='VAT Registration', size=11)
    bin = fields.Char(string='BIN Number', size=13)
    tin = fields.Char(string='TIN Number', size=12)
    fax = fields.Char(string='Fax', size=16)
    nid = fields.Char(string='NID', size=17)
    property_account_receivable_id = fields.Many2one('account.account',string='Account Receivable',
                                                     domain="[('internal_type', '=', 'receivable')]")
    property_account_payable_id = fields.Many2one('account.account',string='Account Payable',
                                                  domain="[('internal_type', '=', 'payable')]")
    vendor_bank_acc = fields.Char(string='Vendor Bank Account')
    division_id = fields.Many2one('bd.division', string='Division')
    district_id = fields.Many2one('bd.district', string='District')
    upazila_id = fields.Many2one('bd.upazila', string='Upazila/Thana')
    postal_code = fields.Many2one('bd.postal.code', 'Postal Code')
    entity_services = fields.Many2many('entity.service', 'service_partner_wizard_rel', 'service_id',
                                       'res_partner_wizard_id',string='Service')
    designation_id = fields.Many2one('vendor.designation', string="Designation")

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.env['res.partner'].search(
                [('name', '=ilike', self.name.strip()), '|', ('active', '=', True), ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.constrains('mobile')
    def _check_numeric_constrain(self):
        if self.mobile and not self.mobile.isdigit():
            raise Warning('[Format Error] Mobile must be numeric!')



    @api.multi
    def act_change_name(self):
        id = self._context['active_id']

        name = self.env['res.partner'].search([('name', '=ilike', self.name)])
        if len(name) > 0:
            raise Warning('[Unique Error] Name must be unique!')

        pending = self.env['history.res.partner'].search([('state', '=', 'pending'), ('line_id', '=', id)])
        if len(pending) > 0:
            raise Warning('[Warning] You already have a pending request!')

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
             'entity_services': [(6, 0, self.entity_services.ids)],
             'request_date': fields.Datetime.now(),
             'line_id': id})
        record = self.env['res.partner'].search(
            [('id', '=', id), '|', ('active', '=', False), ('active', '=', True)])
        if record:
            record.write({'pending': True})

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