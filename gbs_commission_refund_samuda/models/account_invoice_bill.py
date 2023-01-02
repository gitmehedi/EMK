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
            line = self.env['purchase.order.line'].sudo().search([('invoice_id', '=', rec.id), ('order_id.is_commission_claim', '=', True)])
            rec.is_commission_claimed = True if line else False

    @api.depends('is_refund_claimed')
    def _compute_is_refund_claimed(self):
        for rec in self:
            line = self.env['purchase.order.line'].sudo().search([('invoice_id', '=', rec.id), ('order_id.is_refund_claim', '=', True)])
            rec.is_refund_claimed = True if line else False

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        result = super(AccountInvoice, self)._onchange_partner_id()

        self.is_claimed = self._context.get('default_is_claimed', False)
        if self._context.get('default_account_id', False) and self._context.get('default_is_claimed', False):
            self.account_id = self._context.get('default_account_id')

        return result

    def _prepare_invoice_line_from_po_line(self, line):
        invoice_line = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        commission_control_acc = self.env['commission.refund.acc.config'].sudo().search([('company_id', '=', self.env.user.company_id.id)], limit=1)

        if self.type == 'in_invoice' and self.purchase_id:
            # set default account and quantity for refund and commission invoice.
            if self.purchase_id.is_service_order and (self.purchase_id.is_commission_claim or self.purchase_id.is_refund_claim):
                invoice_line['account_id'] = commission_control_acc.commission_control_account_id.id
                invoice_line['quantity'] = line.product_qty

        return invoice_line
