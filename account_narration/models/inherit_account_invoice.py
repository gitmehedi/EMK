from odoo import models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def _prepare_tax_line_vals(self, line, tax):
        res = super(AccountInvoice, self)._prepare_tax_line_vals(line, tax)
        if res:
            res['product_id'] = line.product_id.id
        return res

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        aml = super(AccountInvoice, self).finalize_invoice_move_lines(move_lines)
        narration = None
        for line in aml:
            if not narration:
                narration = line[2]['name']
            if not line[2].get('product_id', False):
                line[2]['name'] = narration
            if line[2].get('tax_line_id', False):
                line[2]['name'] = narration

        return aml
