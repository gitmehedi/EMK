from odoo import fields, models, api

import odoo.addons.decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def _default_direct_vendor_bill(self):
        return self._context.get('direct_vendor_bill')

    direct_vendor_bill = fields.Boolean(default=lambda self: self._default_direct_vendor_bill(), store=False)
    move_ref = fields.Char(string="Move Reference")

    @api.depends('invoice_id', 'direct_vendor_bill', 'purchase_id')
    def _can_edit_bill_line(self):
        for rec in self:
            rec.can_edit_bill_line = False
            if rec.invoice_id.type == 'in_invoice':
                if rec.invoice_id.from_po_form:
                    if self.env.user.has_group(
                            'gbs_vendor_bill_modification.group_vendor_invoice_editor'):
                        rec.can_edit_bill_line = True

                if len(rec.invoice_id.purchase_id) <= 0 and rec.direct_vendor_bill:
                    rec.can_edit_bill_line = True
                if self.env.user.has_group('gbs_vendor_bill_modification.group_vendor_invoice_editor'):
                    rec.can_edit_bill_line = True
            elif rec.invoice_id.type == 'out_refund':
                rec.can_edit_bill_line = True
            elif rec.invoice_id.type == 'in_refund':
                rec.can_edit_bill_line = True

    can_edit_bill_line = fields.Boolean(compute='_can_edit_bill_line', store=False)
    duplc_qty = fields.Float(string='Dup Qty', store=False, digits=dp.get_precision('Product Unit of Measure'))
