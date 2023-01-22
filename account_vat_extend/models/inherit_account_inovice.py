from odoo import models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    vat_selection = fields.Selection([('normal', 'General'),
                                      ('mushok', 'Mushok-6.3'),
                                      ('vds_authority', 'VDS Authority'),
                                      ], string='VAT Selection', default='normal',
                                     readonly=True, required=True, states={'draft': [('readonly', False)]})

    amount_vat_payable = fields.Float('VAT Payable', compute='_compute_amount', store=True, readonly=True, copy=False,
                                     track_visibility='onchange')

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice',
                 'type')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount) for line in self.tax_line_ids if line.tax_id.is_vat)
        self.amount_tds = sum(round_curr(line.amount) for line in self.tax_line_ids if line.tax_id.is_tds)
        self.amount_vat_payable = sum(round_curr(line.amount_vat_payable) for line in self.invoice_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax if self.vat_selection == 'normal' else self.amount_untaxed + self.amount_vat_payable
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    def _prepare_tax_line_vals(self, line, tax):
        round_curr = self.currency_id.round
        vals = super(AccountInvoice, self)._prepare_tax_line_vals(line, tax)
        if self.env['account.tax'].browse(tax['id']).is_vat:
            vals['amount'] = round_curr(line.amount_vat_payable)

        return vals


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    amount_vat_payable = fields.Float('VAT Payable', compute='_compute_price', store=True, readonly=True, copy=False)

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
                 'invoice_id.date_invoice', 'invoice_id.date', 'invoice_id.vat_selection')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        price += self._calculate_tds_value() if self.tds_id and not self.tds_id.price_include else 0.0
        taxes = False

        if self.vat_id:
            taxes = self.vat_id.compute_all(price, currency, self.quantity, product=self.product_id,
                                            partner=self.invoice_id.partner_id)
        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        if self.invoice_id.currency_id and self.invoice_id.company_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(
                date=self.invoice_id._get_currency_rate_date()).compute(price_subtotal_signed,
                                                                        self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign

        self.price_total = taxes['total_included'] if taxes else self.quantity * price
        self.price_tax = taxes['taxes'][0]['amount'] if taxes else 0.0

        if taxes:
            if self.invoice_id.vat_selection == 'mushok':
                if self.vat_id.mushok_amount != 0.0:
                    self.amount_vat_payable = taxes['taxes'][0]['amount'] / (
                                self.vat_id.amount / self.vat_id.mushok_amount)
                else:
                    self.amount_vat_payable = 0

            elif self.invoice_id.vat_selection == 'vds_authority':
                if self.vat_id.vds_amount != 0.0:
                    self.amount_vat_payable = taxes['taxes'][0]['amount'] / (
                                self.vat_id.amount / self.vat_id.vds_amount)
                else:
                    self.amount_vat_payable = 0

            else:
                self.amount_vat_payable = taxes['taxes'][0]['amount']
