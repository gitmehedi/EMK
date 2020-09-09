from odoo import models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        aml = super(AccountInvoice, self).finalize_invoice_move_lines(move_lines)
        narration = None
        for line in aml:
            if not narration:
                narration = line[2]['name']
            if not line[2]['product_id']:
                line[2]['name'] = narration

        return aml
