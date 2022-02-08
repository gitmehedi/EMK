from odoo import fields, models


class InheritedResPartner(models.Model):
    _inherit = 'res.partner'

    nid = fields.Char(string='NID')
    tin = fields.Char(string="TIN")
    vat = fields.Char(string='VAT Registration')
    bin = fields.Char(string='BIN Number')
    tax = fields.Char(string='Trade License')
    tax_zone = fields.Char('Tax Zone')
    tax_circle = fields.Char('Tax Circle')
    tax_location = fields.Char('Tax Location')
    bank_account_number = fields.Char('Bank Account')
    bank_routing = fields.Char('Bank Routing')
