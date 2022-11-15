from odoo import _, api, fields, models
from lxml import etree
from odoo.exceptions import UserError, ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _default_manual_invoice(self):
        if self._context.get('create_edit_button'):
            return True
        else:
            return False

    manual_invoice = fields.Boolean(default=lambda self: self._default_manual_invoice(),store=True)

    @api.model
    def create(self, vals):
        if 'invoice_line_ids' in vals:
            if not vals['invoice_line_ids']:
                raise UserError(
                    _('Invoice lines cannot be empty!'))
        return super(AccountInvoice, self).create(vals)

    from_po_form = fields.Boolean(default=False)

    @api.depends('partner_id')
    def _compute_direct_vendor_bill(self):
        default_direct_vendor_bill = self.env.context.get('default_direct_vendor_bill')
        if default_direct_vendor_bill:
            self.direct_vendor_bill = True
        else:
            self.direct_vendor_bill = False

    direct_vendor_bill = fields.Boolean(compute='_compute_direct_vendor_bill')

    def _prepare_invoice_line_from_po_line(self, line):
        """ Override parent's method to add lc analytic account on invoice line"""
        invoice_line = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        from_po_form = self.env.context.get('default_from_po_form')
        order_line = self.env['purchase.order.line'].browse(invoice_line['purchase_line_id'])
        product = self.env['purchase.order.line'].browse(invoice_line['product_id'])
        order_id = order_line.order_id
        lc_number = order_line.order_id.po_lc_id.name
        if self.type == 'in_invoice' and not order_id.is_service_order and not order_id.cnf_quotation:
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

        if self.partner_id.id != self.purchase_id.partner_id.id:
            raise UserError(_(
                'You need select purchase order of the selected vendor!'
            ))

        new_lines = self.env['account.invoice.line']
        for line in self.purchase_id.order_line - self.invoice_line_ids.mapped('purchase_line_id'):
            data = self._prepare_invoice_line_from_po_line(line)
            if data:
                if data['quantity'] > 0 and data['price_unit'] > 0:
                    new_line = new_lines.new(data)
                    new_line._set_additional_fields(self)
                    new_lines += new_line

        self.invoice_line_ids += new_lines

        # all not cancelled invoice for this order
        order_lines = self.env['purchase.order.line'].search([('order_id', '=', self.purchase_id.id)])
        invoice_lines = self.env['account.invoice.line'].search(
            [('purchase_line_id', 'in', order_lines.ids)])
        total_invoiced = 0
        for line in invoice_lines:
            if line.invoice_id.state != 'cancel':
                total_invoiced = total_invoiced + line.quantity

        total_invoiced = float("{:.4f}".format(total_invoiced))

        pickings = self.env['stock.picking'].search(
            ['|', ('origin', '=', self.purchase_id.name), ('origin', '=', self.purchase_id.po_lc_id.name),
             ('check_mrr_button', '=', True)])

        moves = self.env['stock.move'].search(
            [('picking_id', 'in', pickings.ids), ('state', '=', 'done')])
        total_mrr_qty = float("{:.4f}".format(sum(move.product_qty for move in moves)))
        if total_invoiced != 0 and total_mrr_qty != 0 and total_invoiced >= total_mrr_qty:
            raise UserError(_('All MRR has been billed for this order!'))

        self.purchase_id = False

        return {}

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(AccountInvoice, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                          toolbar=toolbar,
                                                          submenu=submenu)

        doc = etree.XML(res['arch'])
        no_create_edit_button = self.env.context.get('no_create_edit_button')
        if no_create_edit_button:
            if view_type == 'form' or view_type == 'kanban' or view_type == 'tree':
                for node_form in doc.xpath("//kanban"):
                    node_form.set("create", 'false')
                for node_form in doc.xpath("//tree"):
                    node_form.set("create", 'false')
                for node_form in doc.xpath("//form"):
                    node_form.set("create", 'false')

        res['arch'] = etree.tostring(doc)
        return res

    @api.constrains('invoice_line_ids')
    def _check_qty_price(self):
        for rec in self:
            if len(rec.invoice_line_ids) > 0:
                for line in rec.invoice_line_ids:
                    if line.quantity <= 0:
                        raise ValidationError("Line Quantity cannot be 0!")
                    if line.price_unit <= 0:
                        raise ValidationError("Line Unit Price cannot be 0!")

    # overriden odoo method
    @api.onchange('state', 'partner_id', 'invoice_line_ids')
    def _onchange_allowed_purchase_ids(self):
        '''
        The purpose of the method is to define a domain for the available
        purchase orders.
        '''
        result = {}

        # A PO can be selected only if at least one PO line is not already in the invoice
        purchase_line_ids = self.invoice_line_ids.mapped('purchase_line_id')
        purchase_ids = self.invoice_line_ids.mapped('purchase_id').filtered(lambda r: r.order_line <= purchase_line_ids)

        domain = [('invoice_status', 'in', ('to invoice', 'invoiced'))]
        if self.partner_id:
            domain += [('partner_id', 'child_of', self.partner_id.id)]
        if purchase_ids:
            domain += [('id', 'not in', purchase_ids.ids)]
        result['domain'] = {'purchase_id': domain}
        return result
