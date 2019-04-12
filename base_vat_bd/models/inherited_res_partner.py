from odoo import fields, api, models


class InheritedResPartner(models.Model):
    _inherit = 'res.partner'

    tax = fields.Char(string='Trade License')
    vat = fields.Char(string='VAT Registration')
    bin = fields.Char(string='BIN Number')
    tin = fields.Char(string='TIN Number')

    @api.onchange("name")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()
