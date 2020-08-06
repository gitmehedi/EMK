from odoo import api, fields, models, _


class VendorSecurityReturn(models.Model):
    _inherit = 'vendor.security.return'

    def get_deposit_debit_item(self, deposit_line):
        res = super(VendorSecurityReturn, self).get_deposit_debit_item(deposit_line)
        res['sub_operating_unit_id'] = deposit_line.vsd_id.sub_operating_unit_id.id or False
        return res

    def get_supplier_credit_item(self, journal_id):
        res = super(VendorSecurityReturn, self).get_supplier_credit_item(journal_id)
        res['sub_operating_unit_id'] = self.partner_id.property_account_payable_sou_id.id or False
        return res

