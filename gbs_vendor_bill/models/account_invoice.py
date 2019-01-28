# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit',
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid),
                                        readonly=True,required=True,
                                        states={'draft': [('readonly',False)]})
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', 'Sub Branch',
                                        readonly=True,states={'draft': [('readonly',False)]})

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):
        for invoice in self:
            invoice.sub_operating_unit_id = []

    @api.constrains('reference')
    def _check_unique_reference(self):
        if self.partner_id and self.reference:
            filters = [['reference', '=ilike', self.reference.strip()], ['partner_id', '=', self.partner_id.id]]
            bill_no = self.search(filters)
            if len(bill_no) > 1:
                raise UserError(_('Reference must be unique for %s !') % self.partner_id.name)

    # @api.multi
    # def compute_invoice_totals(self, company_currency, invoice_move_lines):
    #     res = super(AccountInvoice, self).compute_invoice_totals(company_currency, invoice_move_lines)
    #     if res:

    # @api.model
    # def invoice_line_move_line_get(self):
    #     res = super(AccountInvoice, self).invoice_line_move_line_get()
    #     return res

    @api.model
    def tax_line_move_line_get(self):
        res = []
        # keep track of taxes already processed
        done_taxes = []
        # loop the invoice.tax.line in reversal sequence
        for tax_line in sorted(self.tax_line_ids, key=lambda x: -x.sequence):
            if tax_line.amount:
                tax = tax_line.tax_id
                if tax.amount_type == "group":
                    for child_tax in tax.children_tax_ids:
                        done_taxes.append(child_tax.id)
                res.append({
                    'invoice_tax_line_id': tax_line.id,
                    'tax_line_id': tax_line.tax_id.id,
                    'type': 'tax',
                    'name': tax_line.name,
                    'price_unit': -tax_line.amount,
                    'quantity': 1,
                    'price': -tax_line.amount,
                    'account_id': tax_line.account_id.id,
                    'account_analytic_id': tax_line.account_analytic_id.id,
                    'invoice_id': self.id,
                    'tax_ids': [(6, 0, list(done_taxes))] if tax_line.tax_id.include_base_amount else []
                })
                done_taxes.append(tax.id)
        return res

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
                 'invoice_id.date_invoice', 'invoice_id.date')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,
                                                          partner=self.invoice_id.partner_id)
        self.price_subtotal = taxes['total_included'] if taxes else self.quantity * price
        self.price_subtotal_without_vat = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        if self.invoice_id.currency_id and self.invoice_id.company_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(
                date=self.invoice_id._get_currency_rate_date()).compute(price_subtotal_signed,
                                                                        self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign

    price_subtotal = fields.Monetary(string='Amount With Vat',
                                     store=True, readonly=True, compute='_compute_price')
    price_subtotal_without_vat = fields.Monetary(string='Amount',
                                     store=True, readonly=True, compute='_compute_price')

    operating_unit_id = fields.Many2one('operating.unit',string='Branch',required=True,
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid))
    sub_operating_unit_id = fields.Many2one('sub.operating.unit',string='Sub Branch')

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):
        for line in self:
            line.sub_operating_unit_id = []
