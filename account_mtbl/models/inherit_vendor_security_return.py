from odoo import api, fields, models, _


class VendorSecurityReturn(models.Model):
    _inherit = 'vendor.security.return'

    def create_account_move(self, journal_id):
        move = super(VendorSecurityReturn, self).create_account_move(journal_id)
        if move:
            for line in move.line_ids:
                line.write({'sub_operating_unit_id': self.company_id.security_deposit_sequence_id.id})
        return move