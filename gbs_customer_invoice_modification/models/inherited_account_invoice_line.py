from odoo import fields, models, api

import odoo.addons.decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.depends('invoice_id', 'partner_id')
    def _can_edit_invoice_line(self):
        for rec in self:
            rec.can_edit_invoice_line = False
            if rec.invoice_id.type == 'out_invoice':
                if self.env.user.has_group('gbs_customer_invoice_modification.group_customer_invoice_editor'):
                    rec.can_edit_invoice_line = True
            elif rec.invoice_id.type == 'out_refund':
                rec.can_edit_invoice_line = True
            elif rec.invoice_id.type == 'in_refund':
                rec.can_edit_invoice_line = True

            create_edit_button = self._context.get('create_edit_button')
            if create_edit_button and self.env.user.has_group(
                    'gbs_customer_invoice_modification.group_customer_invoice_editor'):
                rec.can_edit_invoice_line = True

    can_edit_invoice_line = fields.Boolean(compute='_can_edit_invoice_line', store=False)

    @api.model
    def _default_manual_invoice(self):
        if self._context.get('create_edit_button'):
            return True
        else:
            return False

    manual_invoice = fields.Boolean(default=lambda self: self._default_manual_invoice(), store=True)
