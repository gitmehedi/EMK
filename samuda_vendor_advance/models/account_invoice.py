# import of odoo
from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def assign_outstanding_credit(self, credit_aml_id):
        res = super(AccountInvoice, self).assign_outstanding_credit(credit_aml_id)

        # for adjusted amount of vendor advance
        # for in_invoice type
        # credit_aml_id=debit_aml_id
        credit_aml = self.env['account.move.line'].browse(credit_aml_id)
        vendor_advance = self.env['vendor.advance'].search([('move_id', '=', credit_aml.move_id.id)])
        if credit_aml.user_type_id.type == 'payable' and credit_aml.debit > 0 and vendor_advance:

            if credit_aml.amount_residual <= 0:
                vendor_advance.write({'adjusted_amount': credit_aml.debit, 'state': 'done'})
            else:
                adjusted_amount = credit_aml.debit - credit_aml.amount_residual
                total_adjusted_amount = vendor_advance.adjusted_amount + adjusted_amount
                vendor_advance.write({'adjusted_amount': total_adjusted_amount})

        return res
