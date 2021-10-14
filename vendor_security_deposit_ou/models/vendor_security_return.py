from odoo import api, fields, models


class VendorSecurityReturn(models.Model):
    _inherit = 'vendor.security.return'

    def get_supplier_credit_item(self, journal_id):
        res = super(VendorSecurityReturn, self).get_supplier_credit_item(journal_id)
        ou_id = [line.vsd_id.operating_unit_id.id for line in self.line_ids][0]
        res['operating_unit_id'] = ou_id

        return res

    def get_deposit_debit_item(self, deposit_line):
        res = super(VendorSecurityReturn, self).get_deposit_debit_item(deposit_line)
        res['operating_unit_id'] = deposit_line.vsd_id.operating_unit_id.id

        return res

    def create_account_move(self, journal_id):
        move = super(VendorSecurityReturn, self).create_account_move(journal_id)
        move.write({'operating_unit_id': journal_id.operating_unit_id.id})

        return move
