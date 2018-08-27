# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    # @api.multi
    # def write(self, vals):
    #     MemberLine = self.env['membership.membership_line']
    #     res = super(AccountInvoiceLine, self).write(vals)
    #     for line in self.filtered(lambda line: line.invoice_id.type == 'out_invoice'):
    #         member_lines = MemberLine.search([('account_invoice_line', '=', line.id)])
    #         if line.product_id.membership and not member_lines:
    #             # Product line has changed to a membership product
    #             date_from = line.product_id.membership_date_from
    #             date_to = line.product_id.membership_date_to
    #             if line.invoice_id.date_invoice > date_from and line.invoice_id.date_invoice < date_to:
    #                 date_from = line.invoice_id.date_invoice
    #             MemberLine.create({
    #                 'partner': line.invoice_id.partner_id.id,
    #                 'membership_id': line.product_id.id,
    #                 'member_price': line.price_unit,
    #                 'date': fields.Date.today(),
    #                 'date_from': date_from,
    #                 'date_to': date_to,
    #                 'account_invoice_line': line.id,
    #             })
    #         if line.product_id and not line.product_id.membership and member_lines:
    #             # Product line has changed to a non membership product
    #             member_lines.unlink()
    #     return res

    @api.model
    def create(self, vals):
        MemberLine = self.env['membership.membership_line']
        invoice_line = super(AccountInvoiceLine, self).create(vals)
        if invoice_line.invoice_id.type == 'out_invoice' and \
                invoice_line.product_id.membership:
            inv = MemberLine.search([('account_invoice_line', '=', invoice_line.id)])
            inv.write({'date': '', 'date_from': '', 'date_to': ''})
        return invoice_line
