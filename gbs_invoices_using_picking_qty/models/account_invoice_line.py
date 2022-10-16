from odoo import fields, models, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.depends('invoice_id')
    def _can_edit_bill_line(self):
        for rec in self:
            rec.can_edit_bill_line = False
            if rec.invoice_id.type == 'in_invoice':
                if rec.invoice_id.from_po_form:
                    if self.env.user.has_group(
                            'gbs_invoices_using_picking_qty.group_vendor_invoice_editor') or rec.purchase_id.is_service_order or rec.purchase_id.cnf_quotation:
                        rec.can_edit_bill_line = True
                else:
                    if len(rec.purchase_id) <= 0 or rec.purchase_id.is_service_order or rec.purchase_id.cnf_quotation:
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
