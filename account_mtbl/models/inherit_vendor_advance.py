from odoo import models, fields, api, _


class VendorAdvance(models.Model):
    _name = 'vendor.advance'
    _inherit = ['vendor.advance', 'ir.needaction_mixin']

    operating_unit_id = fields.Many2one('operating.unit', string='Branch')
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Sequence', required=True,
                                            track_visibility='onchange', readonly=True,
                                            states={'draft': [('readonly', False)]})

    @api.onchange('account_id')
    def _onchange_account_id(self):
        for rec in self:
            rec.sub_operating_unit_id = None

    # def create_journal(self, journal_id):
    #     move = super(VendorAdvance, self).create_journal(journal_id)
    #     if self.sub_operating_unit_id:
    #         for line in move.line_ids:
    #             line.write({'sub_operating_unit_id': self.sub_operating_unit_id.id})
    #     return move

    def get_debit_item_data(self, journal_id):
        res = super(VendorAdvance, self).get_debit_item_data(journal_id)
        res['sub_operating_unit_id'] = self.sub_operating_unit_id.id or False
        return res

    def get_deposit_credit_item_data(self, journal_id):
        res = super(VendorAdvance, self).get_deposit_credit_item_data(journal_id)
        res['sub_operating_unit_id'] = self.company_id.security_deposit_sequence_id.id or False
        return res

    def get_vat_item_data(self, vat_id, vat_amount):
        res = super(VendorAdvance, self).get_vat_item_data(vat_id, vat_amount)
        res['sub_operating_unit_id'] = vat_id.sou_id.id or False
        return res

    def get_tds_item_data(self, tds_id, tds_amount):
        res = super(VendorAdvance, self).get_tds_item_data(tds_id, tds_amount)
        res['sub_operating_unit_id'] = tds_id.sou_id.id or False
        return res

    def get_supplier_credit_item_data(self, journal_id, supplier_credit_amount):
        res = super(VendorAdvance, self).get_supplier_credit_item_data(journal_id, supplier_credit_amount)
        res['sub_operating_unit_id'] = self.partner_id.property_account_payable_sou_id.id or False
        return res

    # def create_journal_for_amendment(self, amount, journal_id):
    #     move = super(VendorAdvance, self).create_journal_for_amendment(amount, journal_id)
    #     if self.sub_operating_unit_id:
    #         for line in move.line_ids:
    #             line.write({'sub_operating_unit_id': self.sub_operating_unit_id.id})
    #
    #     return move
