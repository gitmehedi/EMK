from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class InheritedAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    from_po_form = fields.Boolean(default=False)

    #direct_vendor_bill = fields.Boolean()

    def _prepare_invoice_line_from_po_line(self, line):
        """ Override parent's method to add lc analytic account on invoice line"""
        invoice_line = super(InheritedAccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        # get_available_qty

        order_line = self.env['purchase.order.line'].browse(invoice_line['purchase_line_id'])
        product = self.env['purchase.order.line'].browse(invoice_line['product_id'])
        order_id = order_line.order_id
        lc_number = order_line.order_id.po_lc_id.name
        mrr_qty = self.env['account.invoice.utility'].get_mrr_qty(order_id, lc_number, product)
        available_qty = self.env['account.invoice.utility'].get_available_qty(order_id, product.id, mrr_qty)
        invoice_line.update({'quantity': available_qty})

        return invoice_line
