from odoo import fields, api, models


class InheritedResPartner(models.Model):
    _inherit='res.partner'


    """ Relational Fields """

    tax = fields.Char(string='Trade License')
    vat = fields.Char(string='VAT Registration')
    bin = fields.Char(string='BIN Number')
    tin = fields.Char(string='TIN Number')