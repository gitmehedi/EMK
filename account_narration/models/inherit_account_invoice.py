from odoo import models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def _prepare_tax_line_vals(self, line, tax):
        res = super(AccountInvoice, self)._prepare_tax_line_vals(line, tax)
        res['name'] = line.name
        return res

    # @api.multi
    # def finalize_invoice_move_lines(self, move_lines):
    #     aml = super(AccountInvoice, self).finalize_invoice_move_lines(move_lines)
    #     for line in aml:
    #         if line[2]['account_id'] == self.partner_id.property_account_payable_id.id:
    #             # here, set the narration
    #             line[2]['name'] = 'Custom'
    #             break
    #
    #     return aml
