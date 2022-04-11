# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.addons.opa_utility.helper.utility import Message
from odoo.exceptions import ValidationError


class OperatingUnit(models.Model):
    _name = 'operating.unit'
    _inherit = ['operating.unit', 'mail.thread', 'ir.needaction_mixin']
    _description = 'Operating Unit'

    receipt_title = fields.Char(string='Receipt Title', required=True, track_visibility=True)
    receipt_company_title = fields.Char(string='Receipt Company Title', track_visibility=True)
    name = fields.Char(required=True, track_visibility=True)
    code = fields.Char(required=True, track_visibility=True)
    active = fields.Boolean(default=True, track_visibility=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, track_visibility=True,
                                 default=lambda self: self.env['res.company']._company_default_get('account.account'))
    partner_id = fields.Many2one('res.partner', 'Partner', required=True, track_visibility=True)
    street = fields.Char(string='Street', required=True, track_visibility=True)
    street2 = fields.Char(string='Street2', track_visibility=True)
    city = fields.Char(string='City', required=True, track_visibility=True)
    zip = fields.Char(string='Zip', required=True, track_visibility=True)
    vat = fields.Char(string='VAT Reg No', required=True, track_visibility=True)
    email = fields.Char(string='Email', track_visibility=True)
    fax = fields.Char(string='Fax', track_visibility=True)
    contact_no = fields.Char(string='Contact No', required=True, track_visibility=True)
    rule_name = fields.Char(string='Rule Name', required=True, track_visibility=True)

    @api.constrains('code', 'company_id', 'name')
    def _check_code_company(self):
        if self.code and self.company_id:
            code = self.search([('code', '=', self.code), ('company_id', '=', self.company_id.id)])
            if len(code) > 1:
                raise ValidationError(_(Message.UNIQUE_CODE_WARNING))

            name = self.search([('name', '=', self.name), ('company_id', '=', self.company_id.id)])
            if len(name) > 1:
                raise ValidationError(_(Message.UNIQUE_WARNING))

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        names1 = super(models.Model, self).name_search(name=name, args=args, operator=operator, limit=limit)
        names2 = []
        if name:
            domain = [('code', '=ilike', name + '%')]
            names2 = self.search(domain, limit=limit).name_get()
        return list(set(names1) | set(names2))[:limit]

    @api.onchange("receipt_title", "receipt_company_title")
    def onchange_strips(self):
        if self.receipt_title:
            self.receipt_title = str(self.receipt_title.strip()).upper()
        if self.receipt_company_title:
            self.receipt_company_title = str(self.receipt_company_title.strip()).upper()
