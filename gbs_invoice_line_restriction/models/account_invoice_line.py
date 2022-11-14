from odoo import fields, models, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def _default_direct_vendor_bill(self):
        return self._context.get('direct_vendor_bill')

    direct_vendor_bill = fields.Boolean(default=lambda self: self._default_direct_vendor_bill())

    @api.depends('invoice_id', 'direct_vendor_bill', 'purchase_id')
    def _can_edit_bill_line(self):
        for rec in self:
            rec.can_edit_bill_line = False
            if rec.invoice_id.type == 'in_invoice':
                if rec.invoice_id.from_po_form:
                    if self.env.user.has_group(
                            'gbs_invoice_line_restriction.group_vendor_invoice_editor'):
                        rec.can_edit_bill_line = True

                if len(rec.invoice_id.purchase_id) <= 0 and rec.direct_vendor_bill:
                    rec.can_edit_bill_line = True
                if self.env.user.has_group('gbs_invoice_line_restriction.group_vendor_invoice_editor'):
                    rec.can_edit_bill_line = True
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
                if self.env.user.has_group('gbs_invoice_line_restriction.group_customer_invoice_editor'):
                    rec.can_edit_invoice_line = True
            elif rec.invoice_id.type == 'out_refund':
                rec.can_edit_invoice_line = True
            elif rec.invoice_id.type == 'in_refund':
                rec.can_edit_invoice_line = True

    can_edit_invoice_line = fields.Boolean(compute='_can_edit_invoice_line', store=False)
