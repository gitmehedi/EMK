from odoo import api, fields, models, _


class VendorSecurityReturn(models.Model):
    _inherit = 'vendor.security.return'

    def get_deposit_debit_item(self, deposit_line):
        res = super(VendorSecurityReturn, self).get_deposit_debit_item(deposit_line)
        res['sub_operating_unit_id'] = deposit_line.vsd_id.sub_operating_unit_id.id or False
        res['reconcile_ref'] = deposit_line.vsd_id.reconcile_ref
        return res

    def get_supplier_credit_item(self, journal_id):
        res = super(VendorSecurityReturn, self).get_supplier_credit_item(journal_id)
        op_unit = self.env['operating.unit'].search([('code', '=', '001')], limit=1)
        res['operating_unit_id'] = op_unit.id or False
        res['sub_operating_unit_id'] = self.partner_id.property_account_payable_sou_id.id or False
        res['reconcile_ref'] = self.get_reconcile_ref(res['account_id'], res['ref'])
        return res

    def get_reconcile_ref(self, account_id, ref):
        # Generate reconcile ref code
        reconcile_ref = None
        account_obj = self.env['account.account'].search([('id', '=', account_id)])
        if account_obj.reconcile:
            reconcile_ref = account_obj.code + ref.replace('/', '')

        return reconcile_ref

