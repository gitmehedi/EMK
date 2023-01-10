from collections import defaultdict

# imports of odoo
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date, time, timedelta


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    is_commission_claimed = fields.Boolean(
        string="Commission Claimed",
        compute="_compute_is_commission_claimed",
    )
    is_refund_claimed = fields.Boolean(
        string="Refund Claimed",
        compute="_compute_is_refund_claimed",
    )

    is_claimed = fields.Boolean(default=lambda self: self.env.context.get('default_is_claimed') or False, string="Commission/Refund Claimed")

    @api.depends('is_commission_claimed')
    def _compute_is_commission_claimed(self):
        for rec in self:
            line = self.env['purchase.order.line'].sudo().search([
                ('invoice_id', '=', rec.id),
                ('order_id.is_commission_claim', '=', True),
                ('order_id.state', '!=', 'cancel')
            ])
            rec.is_commission_claimed = True if line else False

    @api.depends('is_refund_claimed')
    def _compute_is_refund_claimed(self):
        for rec in self:
            line = self.env['purchase.order.line'].sudo().search([
                ('invoice_id', '=', rec.id),
                ('order_id.is_refund_claim', '=', True),
                ('order_id.state', '!=', 'cancel')
            ])
            rec.is_refund_claimed = True if line else False

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        result = super(AccountInvoice, self)._onchange_partner_id()

        self.is_claimed = self._context.get('default_is_claimed', False)
        if not self.is_claimed and self.partner_id:
            self.account_id = self.partner_id.property_account_payable_id.id
        else:
            self.account_id = self._context.get('default_account_id')

        return result

    def _prepare_invoice_line_from_po_line(self, line):
        invoice_line = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        commission_control_acc = self.env['commission.refund.acc.config'].sudo().search([('company_id', '=', self.env.user.company_id.id)], limit=1)

        if self.type == 'in_invoice' and self.purchase_id:
            # set default account and quantity for refund and commission invoice.
            if self.purchase_id.is_service_order and (self.purchase_id.is_commission_claim or self.purchase_id.is_refund_claim):
                invoice_line['account_id'] = commission_control_acc.commission_control_account_id.id

                qty= 0
                for inv_line in line.invoice_lines:
                    if inv_line.invoice_id.state not in ['cancel']:
                        if inv_line.invoice_id.type == 'in_invoice':
                            qty += inv_line.quantity
                invoice_line['quantity'] = line.product_qty - qty

        return invoice_line
