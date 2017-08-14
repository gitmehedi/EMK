from odoo import fields, api, models


class InheritedResPartner(models.Model):
    _inherit='res.partner'


    """ Relational Fields """

    tax = fields.Char(string='Trade License')
    vat = fields.Char(string='VAT Registration')