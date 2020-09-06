from odoo import models, fields, api, _
from odoo.exceptions import Warning


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_account_payable_sou_id = fields.Many2one('sub.operating.unit', string='Sequence', copy=False,
                                                      track_visibility='onchange', required=True)

    @api.constrains('name')
    def _constrains_name(self):
        # Check for Unique Name
        if self.name:
            vendor_id = self.search([('name', '=ilike', self.name.strip()), ('supplier', '=', True)])
            if len(vendor_id.ids) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.constrains('vendor_bank_acc')
    def _constrains_vendor_bank_acc(self):
        if self.vendor_bank_acc:
            if len(self.vendor_bank_acc) != 13:
                raise Warning('Vendor Bank Account must be 13 digit.')

            if not self.vendor_bank_acc.isdigit():
                raise Warning('[Format Error] Vendor Account must be numeric!')

    @api.onchange('vendor_bank_acc')
    def _onchange_vendor_bank_acc(self):
        if self.vendor_bank_acc and not self.vendor_bank_acc.isdigit():
            raise Warning('Vendor Bank Account must be numeric!')

    @api.onchange('property_account_payable_id')
    def _onchange_property_account_payable_id(self):
        for rec in self:
            rec.property_account_payable_sou_id = None
