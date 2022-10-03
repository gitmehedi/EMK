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
                    pickings = self.env['stock.picking'].search(
                        [('origin', '=', order_id.name), ('check_mrr_button', '=', True)])

                    moves = self.env['stock.move'].search(
                        [('picking_id', 'in', pickings.ids), ('product_id', 'in', rec.product_id.ids),
                         ('state', '=', 'done')])
                    total_mrr_qty = sum(move.product_qty for move in moves)
                    if total_mrr_qty <= 0:
                        raise UserError(_('MRR not done for this order!'))
                    rec.mrr_qty = total_mrr_qty

    mrr_qty = fields.Float(compute='calc_mrr_qty', store=True, readonly=False)

    @api.depends('purchase_line_id', 'product_id', 'mrr_qty')
    def calc_available_qty(self):
        for rec in self:
            rec.available_qty = False
            if rec.invoice_id.type == 'in_invoice' and not rec.purchase_id.is_service_order and not rec.purchase_id.cnf_quotation and rec.invoice_id.from_po_form:
                if rec.purchase_line_id and rec.product_id:
                    order_id = rec.purchase_line_id.order_id
                    invoice_id = self.env.context.get('active_id')
                    other_invoices = order_id.invoice_ids.filtered(lambda x: x.state != 'cancel')
                    pro_qty_invoiced = 0
                    for inv in other_invoices:
                        for line in inv.invoice_line_ids:
                            if line.product_id.id == rec.product_id.id:
                                pro_qty_invoiced = pro_qty_invoiced + line.quantity
                    rec.available_qty = rec.mrr_qty - pro_qty_invoiced

    available_qty = fields.Float(compute='calc_available_qty', store=True, readonly=False)

    @api.model
    @api.depends('available_qty')
    def _get_default_qty(self):
        if self.invoice_id.type == 'in_invoice' and not self.purchase_id.is_service_order and not self.purchase_id.cnf_quotation and self.invoice_id.from_po_form:
            if self.available_qty:
                return self.available_qty
        else:
            return self.purchase_line_id.product_qty

    @api.constrains('quantity')
    def _check_quantity(self):
        if self.invoice_id.type == 'in_invoice' and not self.purchase_id.is_service_order and not self.purchase_id.cnf_quotation and self.invoice_id.from_po_form:
            if self.quantity <= 0:
                raise UserError(_("Quantity cannot be zero or less than 0!"))
            # mrr qty - ei porjonto joto qty == 0
            if self.purchase_line_id and self.product_id:
                order_id = self.purchase_line_id.order_id
                invoice_id = self.env.context.get('active_id')
                other_invoices = order_id.invoice_ids.filtered(lambda x: x.state != 'cancel')
                pro_qty_invoiced = 0
                for inv in other_invoices:
                    for line in inv.invoice_line_ids:
                        if line.product_id.id == self.product_id.id:
                            pro_qty_invoiced = pro_qty_invoiced + line.quantity
                if pro_qty_invoiced > self.mrr_qty:
                    raise UserError(_("Quantity cannot be greater than available MRR!"))

    # overriding quantity field
    quantity = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'),
                            required=True, readonly=False, default=_get_default_qty)

    def check_group_vendor_invoice_editor(self):
        for rec in self:
            rec.can_edit_bill_line = False
            if rec.invoice_id.type == 'in_invoice':
                if self.env.user.has_group('gbs_invoices_using_picking_qty.group_vendor_invoice_editor'):
                    rec.can_edit_bill_line = True
            if rec.purchase_id.is_service_order:
                rec.can_edit_invoice_line = True
            if rec.purchase_id.cnf_quotation:
                rec.can_edit_invoice_line = True
            if not rec.invoice_id.from_po_form:
                rec.can_edit_invoice_line = True

    can_edit_bill_line = fields.Boolean(compute='check_group_vendor_invoice_editor', store=False)

    def check_group_customer_invoice_editor_editor(self):
        for rec in self:
            rec.can_edit_invoice_line = False
            if rec.invoice_id.type == 'out_invoice':
                if self.env.user.has_group('gbs_invoices_using_picking_qty.group_customer_invoice_editor'):
                    rec.can_edit_invoice_line = True
            if rec.purchase_id.is_service_order:
                rec.can_edit_invoice_line = True
            if rec.purchase_id.cnf_quotation:
                rec.can_edit_invoice_line = True
            if not rec.invoice_id.from_po_form:
                rec.can_edit_invoice_line = True

    can_edit_invoice_line = fields.Boolean(compute='check_group_customer_invoice_editor_editor', store=False)
