from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import odoo.addons.decimal_precision as dp


class InheritedAccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.depends('purchase_line_id', 'product_id')
    def calc_mrr_qty(self):
        for rec in self:
            rec.mrr_qty = False
            if rec.invoice_id.type == 'in_invoice' and not rec.purchase_id.is_service_order and not rec.purchase_id.cnf_quotation and rec.invoice_id.from_po_form:
                if rec.purchase_line_id and rec.product_id:
                    order_id = rec.purchase_line_id.order_id
                    lc_number = rec.purchase_id.po_lc_id.name

                    rec.mrr_qty = self.env['account.invoice.utility'].get_mrr_qty(order_id, lc_number,
                                                                                  rec.product_id)

    mrr_qty = fields.Float(compute='calc_mrr_qty', store=True, readonly=False)

    @api.depends('purchase_line_id', 'product_id', 'mrr_qty')
    def calc_available_qty(self):
        for rec in self:
            rec.available_qty = False
            if rec.invoice_id.type == 'in_invoice' and not rec.purchase_id.is_service_order and not rec.purchase_id.cnf_quotation and rec.invoice_id.from_po_form:
                if rec.purchase_line_id and rec.product_id:
                    order_id = rec.purchase_line_id.order_id
                    rec.available_qty = self.env['account.invoice.utility'].get_available_qty(order_id,
                                                                                              rec.product_id.id,
                                                                                              rec.mrr_qty)

    available_qty = fields.Float(compute='calc_available_qty', store=True, readonly=False)

    @api.model
    @api.depends('available_qty')
    def _get_default_qty(self):
        for rec in self:
            if rec.invoice_id.type == 'in_invoice' and not rec.purchase_id.is_service_order and not rec.purchase_id.cnf_quotation and rec.invoice_id.from_po_form:
                if rec.available_qty:
                    return rec.available_qty
            else:
                return rec.purchase_line_id.product_qty

    @api.constrains('mrr_qty')
    def _check_mrr_qty(self):
        for rec in self:
            if rec.mrr_qty <= 0:
                raise UserError(_("MRR not done!"))

    @api.constrains('price_unit')
    def _check_price_unit(self):
        for rec in self:
            if rec.price_unit <= 0:
                raise UserError(_("Unit Price cannot be zero or less than 0!"))

    @api.constrains('quantity')
    def _check_quantity(self):
        for rec in self:
            if rec.quantity <= 0:
                raise UserError(_("Quantity cannot be zero or less than 0!"))
            if rec.invoice_id.type == 'in_invoice' and not rec.purchase_id.is_service_order and not rec.purchase_id.cnf_quotation and rec.invoice_id.from_po_form:
                # mrr qty - ei porjonto joto qty == 0
                if rec.purchase_line_id and rec.product_id:
                    order_id = rec.purchase_line_id.order_id
                    invoice_id = self.env.context.get('active_id')
                    other_invoices = order_id.invoice_ids.filtered(lambda x: x.state != 'cancel')
                    pro_qty_invoiced = 0
                    for inv in other_invoices:
                        for line in inv.invoice_line_ids:
                            if line.product_id.id == rec.product_id.id:
                                pro_qty_invoiced = pro_qty_invoiced + line.quantity
                    if pro_qty_invoiced > rec.mrr_qty:
                        raise UserError(_("Quantity cannot be greater than available MRR!"))

    # overriding quantity field
    quantity = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'),
                            required=True, readonly=False, default=_get_default_qty)

    @api.depends('invoice_id')
    def _can_edit_bill_line(self):
        for rec in self:
            # new id check:
            # if not isinstance(rec.invoice_id.id, int):
            #     rec.can_edit_bill_line = True-
            # else:

            rec.can_edit_bill_line = False
            if rec.invoice_id.type == 'in_invoice':
                if self.env.user.has_group(
                        'gbs_invoices_using_picking_qty.group_vendor_invoice_editor') or rec.purchase_id.is_service_order or rec.purchase_id.cnf_quotation:
                    rec.can_edit_bill_line = True
                if not rec.invoice_id.from_po_form:
                    if len(rec.purchase_id) <= 0:
                        rec.can_edit_bill_line = True
            # if rec.invoice_id.type == 'in_invoice':
            #     rec.can_edit_bill_line = True
            elif rec.invoice_id.type == 'out_refund':
                rec.can_edit_bill_line = True
            elif rec.invoice_id.type == 'in_refund':
                rec.can_edit_bill_line = True

    can_edit_bill_line = fields.Boolean(compute='_can_edit_bill_line', store=False)

    @api.depends('invoice_id')
    def _can_edit_invoice_line(self):
        for rec in self:
            rec.can_edit_invoice_line = False
            if rec.invoice_id.type == 'out_invoice':
                if self.env.user.has_group('gbs_invoices_using_picking_qty.group_customer_invoice_editor'):
                    rec.can_edit_invoice_line = True
            elif rec.invoice_id.type == 'out_refund':
                rec.can_edit_invoice_line = True
            elif rec.invoice_id.type == 'in_refund':
                rec.can_edit_invoice_line = True

    can_edit_invoice_line = fields.Boolean(compute='_can_edit_invoice_line', store=False)
