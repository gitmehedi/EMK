# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class OperatingUnit(models.Model):
    _name = 'operating.unit'
    _description = 'Operating Unit'

    receipt_title = fields.Char(string='Receipt Title', required=True)
    receipt_company_title = fields.Char(string='Receipt Company Title')
    name = fields.Char(required=True)
    code = fields.Char(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self:
        self.env['res.company']._company_default_get('account.account'))
    partner_id = fields.Many2one('res.partner', 'Partner', required=True)

    street = fields.Char(string='Street', required=True)
    street2 = fields.Char(string='Street2')
    city = fields.Char(string='City', required=True)
    zip = fields.Char(string='Zip', required=True)
    vat = fields.Char(string='VAT Reg No', required=True)
    email = fields.Char(string='Email')
    fax = fields.Char(string='Fax')
    contact_no = fields.Char(string='Contact No', required=True)

    _sql_constraints = [
        ('code_company_uniq', 'unique (code,company_id)',
         'The code of the operating unit must '
         'be unique per company!'),
        ('name_company_uniq', 'unique (name,company_id)',
         'The name of the operating unit must '
         'be unique per company!')
    ]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        names1 = super(models.Model, self).name_search(name=name, args=args, operator=operator, limit=limit)
        names2 = []
        if name:
            domain = [('code', '=ilike', name + '%')]
            names2 = self.search(domain, limit=limit).name_get()
        return list(set(names1) | set(names2))[:limit]

    @api.onchange("receipt_title","receipt_company_title")
    def onchange_strips(self):
        if self.receipt_title:
            self.receipt_title = str(self.receipt_title.strip()).upper()
        if self.receipt_company_title:
            self.receipt_company_title = str(self.receipt_company_title.strip()).upper()