from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class InheritedAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _prepare_invoice_line_from_po_line(self, line):
        """ Override parent's method to add lc analytic account on invoice line"""
        invoice_line = super(InheritedAccountInvoice, self)._prepare_invoice_line_from_po_line(line)

        if line.product_qty:
            invoice_line.update({'quantity': line.product_qty})

        if self.type == 'in_invoice' and self.purchase_id:
            if self.purchase_id.region_type == 'foreign' or self.purchase_id.is_service_order:
                if self.purchase_id.lc_ids:
                    analytic_account_id = self.purchase_id.lc_ids[0].analytic_account_id.id
                    if analytic_account_id:
                        invoice_line.update({'account_analytic_id': analytic_account_id})  # update the dictionary
            elif self.purchase_id.cnf_quotation:
                analytic_account_id = self.purchase_id.shipment_id.lc_id.analytic_account_id.id
                if analytic_account_id:
                    invoice_line.update({'account_analytic_id': analytic_account_id})  # update the dictionary

            if self.purchase_id.region_type == 'foreign':
                account_conf_pool = self.env.user.company_id
                if not account_conf_pool.lc_pad_account:
                    raise UserError(
                        _("LC PAD Account not set. Please contact your system administrator for "
                          "assistance."))
                invoice_line.update({'account_id': account_conf_pool.lc_pad_account.id})  # update the dictionary

        return invoice_line
