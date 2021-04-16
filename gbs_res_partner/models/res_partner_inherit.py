from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_account_receivable_id = fields.Many2one(required=False)
    property_account_payable_id = fields.Many2one(required=False)

    tax = fields.Char(string='Trade License')
    vat = fields.Char(string='VAT Registration')
    bin = fields.Char(string='BIN Number')
    tin = fields.Char(string='TIN Number')
