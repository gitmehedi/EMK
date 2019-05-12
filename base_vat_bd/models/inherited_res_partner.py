from odoo import fields, api, models


class InheritedResPartner(models.Model):
    _inherit = 'res.partner'

    tax = fields.Char(string='Trade License')
    vat = fields.Char(string='VAT Registration')
    bin = fields.Char(string='BIN Number',size=13)
    tin = fields.Char(string='TIN Number',size=13)

    @api.onchange("name")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()

    @api.constrains('bin','tin')
    def _check_numeric_constrain(self):
        if self.bin and not self.bin.isdigit():
            raise Warning('[Format Error] BIN must be numeric!')
        if self.tin and not self.tin.isdigit():
            raise Warning('[Format Error] TIN must be numeric!')
