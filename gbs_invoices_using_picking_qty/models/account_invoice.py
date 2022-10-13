from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    from_po_form = fields.Boolean(default=False)

    direct_vendor_bill = fields.Boolean()

    def _prepare_invoice_line_from_po_line(self, line):
        """ Override parent's method to add lc analytic account on invoice line"""
        invoice_line = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        from_po_form = self.env.context.get('default_from_po_form')
        order_line = self.env['purchase.order.line'].browse(invoice_line['purchase_line_id'])
        product = self.env['purchase.order.line'].browse(invoice_line['product_id'])
        order_id = order_line.order_id
        lc_number = order_line.order_id.po_lc_id.name
        if self.type == 'in_invoice' and not order_id.is_service_order and not order_id.cnf_quotation and from_po_form:
            if order_line and product:
                mrr_qty = self.env['account.invoice.utility'].get_mrr_qty(order_id, lc_number, product)
                available_qty = self.env['account.invoice.utility'].get_available_qty(order_id, product.id, mrr_qty)
                # if available_qty  is 0 then don't load
                if available_qty <= 0:
                    return False

                invoice_line.update({'quantity': available_qty})

        return invoice_line

    # replacing odoo original method
    @api.onchange('purchase_id')
    def purchase_order_change(self):
        # res = super(AccountInvoice, self).purchase_order_change()
        if not self.purchase_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.purchase_id.partner_id.id

        new_lines = self.env['account.invoice.line']
        for line in self.purchase_id.order_line - self.invoice_line_ids.mapped('purchase_line_id'):
            data = self._prepare_invoice_line_from_po_line(line)
            if data:
                new_line = new_lines.new(data)
                new_line._set_additional_fields(self)
                new_lines += new_line

        self.invoice_line_ids += new_lines
        self.purchase_id = False
        return {}
