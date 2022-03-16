from odoo import api, fields, models


class VendorAdvance(models.Model):
    _inherit = 'vendor.advance'

    operating_unit_id = fields.Many2one('operating.unit', string='Branch',
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid),
                                        readonly=True, required=True,
                                        states={'draft': [('readonly', False)]})

    def create_journal(self, journal_id):
        move = super(VendorAdvance, self).create_journal(journal_id)
        journal_ou = journal_id.operating_unit_id.id if journal_id.operating_unit_id else self.operating_unit_id.id
        move.write({'operating_unit_id': journal_ou})
        return move

    def get_debit_item_data(self, journal_id):
        res = super(VendorAdvance, self).get_debit_item_data(journal_id)
        res['operating_unit_id'] = self.operating_unit_id.id

        return res

    def get_deposit_credit_item_data(self, journal_id):
        res = super(VendorAdvance, self).get_deposit_credit_item_data(journal_id)
        res['operating_unit_id'] = self.company_id.security_deposit_operating_unit_id.id\
            if self.company_id.security_deposit_operating_unit_id else self.operating_unit_id.id

        return res

    def get_supplier_credit_item_data(self, journal_id, supplier_credit_amount):
        res = super(VendorAdvance, self).get_supplier_credit_item_data(journal_id, supplier_credit_amount)
        res['operating_unit_id'] = self.operating_unit_id.id

        return res

    def get_vat_item_data(self, vat_id, vat_amount):
        res = super(VendorAdvance, self).get_vat_item_data(vat_id, vat_amount)
        res['operating_unit_id'] = vat_id.operating_unit_id.id if vat_id.operating_unit_id\
            else self.operating_unit_id.id

        return res

    def get_tds_item_data(self, tds_id, tds_amount):
        res = super(VendorAdvance, self).get_tds_item_data(tds_id, tds_amount)
        res['operating_unit_id'] = tds_id.operating_unit_id.id if tds_id.operating_unit_id\
            else self.operating_unit_id.id

        return res

    def create_security_deposit(self):
        security_deposit = super(VendorAdvance, self).create_security_deposit()
        security_deposit_ou = self.company_id.security_deposit_operating_unit_id.id\
            if self.company_id.security_deposit_operating_unit_id else self.operating_unit_id.id
        security_deposit.write({'operating_unit_id': security_deposit_ou})
        return security_deposit
