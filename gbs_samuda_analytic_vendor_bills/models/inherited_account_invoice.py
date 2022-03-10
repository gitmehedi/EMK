from odoo import fields, models, api


class InheritedAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _prepare_invoice_line_from_po_line(self, line):
        """ Override parent's method to add lc analytic account on invoice line"""
        invoice_line = super(InheritedAccountInvoice, self)._prepare_invoice_line_from_po_line(line)

        if self.type == 'in_invoice' and self.purchase_id:
            if self.purchase_id.region_type == 'foreign' or self.purchase_id.cnf_quotation or self.purchase_id.is_service_order:
                if self.purchase_id.lc_ids:
                    analytic_account_id = self.purchase_id.lc_ids[0].analytic_account_id.id
                    if analytic_account_id:
                        invoice_line.update({'account_analytic_id': analytic_account_id})  # update the dictionary

        return invoice_line
