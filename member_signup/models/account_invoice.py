# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'


    @api.model
    def create(self, vals):
        MemberLine = self.env['membership.membership_line']
        invoice_line = super(AccountInvoiceLine, self).create(vals)
        if invoice_line.invoice_id.type == 'out_invoice' and \
                invoice_line.product_id.membership:
            inv = MemberLine.search([('account_invoice_line', '=', invoice_line.id)])
            inv.write({'date': '', 'date_from': '', 'date_to': ''})
        return invoice_line
