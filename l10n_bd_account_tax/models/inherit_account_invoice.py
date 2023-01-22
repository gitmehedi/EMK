from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    amount_tax = fields.Monetary(string='VAT')
    amount_tds = fields.Float(string='TDS', compute='_compute_amount', store=True, readonly=True, copy=False,
                              track_visibility='always')
    date_invoice = fields.Date(required=True, default=fields.Date.today())
    amount_vat_payable = fields.Float('VAT Payable', compute='_compute_amount', store=True, readonly=True, copy=False,
                                      track_visibility='onchange')
    vat_selection = fields.Selection([('normal', 'General'),
                                      ('mushok', 'Mushok-6.3'),
                                      ('vds_authority', 'VDS Authority'),
                                      ], string='VAT Selection', default='normal',
                                     readonly=True, required=True, states={'draft': [('readonly', False)]})

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'invoice_line_ids.price_unit', 'invoice_line_ids.quantity',
                 'tax_line_ids.amount', 'currency_id', 'date_invoice',
                 'type')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        # self.amount_tax = sum(round_curr(line.amount) for line in self.tax_line_ids if line.tax_id.is_vat)
        self.amount_tax = sum(round_curr(line.price_tax) for line in self.invoice_line_ids)
        self.amount_tds = sum(round_curr(line.amount) for line in self.tax_line_ids if line.tax_id.is_tds)
        self.amount_vat_payable = sum(round_curr(line.amount_vat_payable) for line in self.invoice_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax
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

    # This function is used to create the account.move.line from account.invoice.line
    # and it is inherited to consider tax amount as an expense value
    # Last Edited Date: 2020-06-03
    # Last Edited By: Abu Rayhan
    @api.model
    def invoice_line_move_line_get(self):
        res = super(AccountInvoice, self).invoice_line_move_line_get()
        new_res = []
        for r in res:
            for line in self.invoice_line_ids:
                if line.id == r.get('invl_id', False):
                    price = line.price_subtotal_signed
                    for tax in line.invoice_line_tax_ids:
                        if len(tax.children_tax_ids) > 0:
                            for ctax in tax.children_tax_ids:
                                if ctax.include_in_expense:
                                    if ctax.is_vat:
                                        price += line.price_tax
                                    else:
                                        price += line.price_tds
                        else:
                            if tax.include_in_expense:
                                if tax.is_vat:
                                    price += line.price_tax
                                else:
                                    price += line.price_tds
                    r['price'] = price
                    break
            new_res.append(r)
        return new_res

    # This function is inherited to decide whether the tax amount will be debited or credited
    # Last Edited Date: 2020-05-22
    # Last Edited By: Matiar Rahman
    @api.model
    def tax_line_move_line_get(self):
        res = super(AccountInvoice, self).tax_line_move_line_get()
        tax_pool = self.env['account.tax']
        new_res = []
        for r in res:
            tax = tax_pool.search([('id', '=', r['tax_line_id'])])[0]
            tax_amount = r['price']
            tax_amount = (tax_amount * -1) if tax.is_reverse else tax_amount
            r['price'] = r['price_unit'] = tax_amount
            tax_type = 'vat' if tax.is_vat else 'tds'
            r['tax_type'] = tax_type
            r['is_tdsvat_payable'] = self.type in ('out_invoice', 'in_invoice') and True
            new_res.append(r)
        return new_res

    # Remove the Function
    @api.multi
    def action_invoice_open(self):
        if self.state == 'draft':
            if self.env.user.id == self.user_id.id and self.env.user.id != SUPERUSER_ID:
                raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))
            self.create_tds_line()
            return super(AccountInvoice, self).action_invoice_open()
        else:
            raise ValidationError(_("[Validation Error] Vendor Bill {} already validated.".format(self.number)))

    # # # Calculate TDS for Slab
    def _calculate_slab_tds(self, line):
        tds_amount = 0
        inv_line = self.get_curr_inv_amount()

        for tds_id, rec in inv_line.items():
            if tds_id != line.tds_id.id:
                continue

            prev_slab = self.env['account.tax.slab.line'].get_prev_slab_inv(self.partner_id, tds_id, self.date_invoice)
            prev_inv_amount = prev_slab['prev_inv_amount']
            prev_tds_amount = prev_slab['prev_tds_amount']
            remain_tds_amount = self.get_remain_tds_amount(prev_inv_amount, prev_tds_amount, rec, tds_id)

            if remain_tds_amount < 0.0:
                tds_amount = 0.0
            elif remain_tds_amount > self.amount_untaxed:
                tds_amount = self.amount_untaxed
            else:
                tds_amount = remain_tds_amount

        line_tds_amount = 0
        inv_amount = inv_line[line.tds_id.id]['inv_amount']
        if inv_amount > 0:
            new_tds_rate = (tds_amount * 100) / inv_amount
            line_tds_amount = line.price_subtotal * (new_tds_rate / 100)

        return round(line_tds_amount, 2)

    def get_remain_tds_amount(self, prev_inv_amount, prev_tds_amount, rec, tds_id):
        total_inv_amount = prev_inv_amount + rec['inv_amount']
        slab_rate = self.get_slab_rate(tds_id, total_inv_amount)
        curr_tds_amount = total_inv_amount * (slab_rate / 100)
        remain_tds_amount = curr_tds_amount - prev_tds_amount
        return round(remain_tds_amount, 2)

    def get_curr_inv_amount(self):
        inv_line = {}
        for val in self.invoice_line_ids:

            if not val.tds_id and val.tds_id.amount_type != 'slab':
                continue
            tds = val.tds_id.id
            amount = val.price_subtotal
            if tds in inv_line:
                inv_line[tds]['inv_amount'] = inv_line[tds]['inv_amount'] + amount
            else:
                inv_line[tds] = {}
                inv_line[tds]['product_id'] = val.product_id.id
                inv_line[tds]['quantity'] = val.quantity
                inv_line[tds]['price_unit'] = val.price_unit
                inv_line[tds]['tds_id'] = val.tds_id
                inv_line[tds]['inv_amount'] = amount
                inv_line[tds]['tds_amount'] = 0
        return inv_line

    def get_prev_inv_amount(self, tds_id):
        fy = self.get_fy()
        prev_obj = self.env['account.tax.slab.line'].search(
            [('partner_id', '=', self.partner_id.id), ('tax_fy_id', '=', fy.id), ('tax_id', '=', tds_id)])
        prev_inv_amount = sum([inv.invoice_amount for inv in prev_obj])
        prev_tds_amount = sum([inv.tds_amount for inv in prev_obj])
        return {'prev_inv_amount': prev_inv_amount, 'prev_tds_amount': prev_tds_amount}

    def create_tds_line(self):
        inv_line = self.get_curr_inv_amount()
        self.env['account.tax.slab.line'].create_slab_line(inv_line, self)

    def get_fy(self, date):
        # The date will not be system date, it will be invoice date
        fy = self.env['date.range'].search(
            [('date_start', '<=', date), ('date_end', '>=', date), ('type_id.tds_year', '=', True),
             ('active', '=', True)], order='id DESC', limit=1)
        if not fy:
            raise ValidationError(_('Please create a TDS year'))
        return fy

    def get_slab_rate(self, tds_id, amount):
        slab_rate = self.env['account.tax.line'].search(
            [('tax_id', '=', tds_id), ('range_from', '<=', amount), ('range_to', '>=', amount)])
        return slab_rate.rate

    def _prepare_tax_line_vals(self, line, tax):
        round_curr = self.currency_id.round
        vals = super(AccountInvoice, self)._prepare_tax_line_vals(line, tax)
        vat_id = self.env['account.tax'].browse(tax['id'])
        if vat_id.is_vat and vat_id.is_reverse:
            vals['amount'] = round_curr(line.amount_vat_payable)

        return vals

    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        round_curr = self.currency_id.round
        for line in self.invoice_line_ids:
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            price_unit += line._calculate_tds_value() if line.tds_id and line.tds_id.effect_base_price else 0.0
            taxes = \
                line.vat_id.compute_all(price_unit, self.currency_id, line.quantity, line.product_id, self.partner_id)[
                    'taxes']
            tds_taxes = \
                line.tds_id.compute_all(price_unit, self.currency_id, line.quantity, line.product_id, self.partner_id)[
                    'taxes']
            if tds_taxes:
                if line.tds_id.amount_type == 'slab':
                    tds_amount = self._calculate_slab_tds(line)
                else:
                    tds_amount = line._calculate_tds_value()

                tds_taxes[0]['amount'] = tds_amount
                tds_taxes[0][
                    'base'] = line.price_subtotal if line.tds_id.price_include else line.quantity * line.price_unit
                taxes += tds_taxes

            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)

                if key not in tax_grouped:
                    tax_grouped[key] = val
                    tax_grouped[key]['base'] = round_curr(val['base'])
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += round_curr(val['base'])

        return tax_grouped


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
                 'invoice_id.date_invoice', 'invoice_id.date', 'invoice_id.vat_selection')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        self.price_tds = self._calculate_tds_value() if self.tds_id and not self.tds_id.price_include else 0.0
        # price += self._calculate_tds_value() if self.tds_id and not self.tds_id.price_include else 0.0
        price += (self.price_tds / self.quantity) if self.quantity > 0 else 0.00
        taxes = False

        if self.vat_id:
            taxes = self.vat_id.compute_all(price, currency, self.quantity, product=self.product_id,
                                            partner=self.invoice_id.partner_id)
            ##### This part is for advacne vat logic i.e. Mushuk and VAT Authority
            ##### This part is re-write by Matiar Rahman
            if taxes:
                amount_vat_payable = 0
                tax_pool = self.env['account.tax']
                for tx in taxes['taxes']:
                    taxobj = tax_pool.browse(tx['id'])
                    if taxobj.is_reverse:
                        if self.invoice_id.vat_selection == 'mushok':
                            if taxobj.mushok_amount != 0.0:
                                amount_vat_payable += tx['amount'] / (taxobj.amount / taxobj.mushok_amount)
                        elif self.invoice_id.vat_selection == 'vds_authority':
                            if taxobj.vds_amount != 0.0:
                                amount_vat_payable += tx['amount'] / (self.vat_id.amount / self.vat_id.vds_amount)
                        else:
                            amount_vat_payable += tx['amount']

                self.amount_vat_payable = amount_vat_payable
            ##############################################################################

        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        self.price_tax = self.get_price_tax(taxes) if taxes else 0.0
        self.price_total = taxes['total_included'] if taxes else self.quantity * price
        if self.invoice_id.currency_id and self.invoice_id.company_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(
                date=self.invoice_id._get_currency_rate_date()).compute(price_subtotal_signed,
                                                                        self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign

    @api.multi
    def get_price_tax(self, taxes):
        price_tax = 0.0
        if self.vat_id.amount_type == 'group':
            for tax in taxes['taxes']:
                tax_id = self.env['account.tax'].browse(tax['id'])
                price_tax += tax['amount'] if tax_id.is_reverse else 0.0
        else:
            price_tax += sum(tax['amount'] for tax in taxes['taxes'])

        return price_tax

    # This function is written by Matiar Rahman
    # And also blocked by Matiar Rahman
    # This will may needed later for expense accounting
    # @api.one
    # @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
    #              'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
    #              'invoice_id.date_invoice', 'invoice_id.date')
    # def _compute_price(self):
    #     res = super(AccountInvoiceLine, self)._compute_price()
    #     taxes = self.invoice_line_tax_ids.compute_all(self.price_unit, self.invoice_id.currency_id, self.quantity,
    #                                                   product=self.product_id, partner=self.invoice_id.partner_id)
    #     self.update({
    #         'price_tax': taxes['total_included'] - taxes['total_excluded'],
    #         'price_total': taxes['total_included'],
    #         # 'price_subtotal': taxes['total_excluded'],
    #     })

    vat_id = fields.Many2one('account.tax', string='VAT')
    tds_id = fields.Many2one('account.tax', string='TDS')
    price_total = fields.Monetary(compute='_compute_price', string='Total', store=True)
    price_tax = fields.Monetary(compute='_compute_price', string='Tax', store=True)
    price_tds = fields.Monetary(compute='_compute_price', string='TDS', store=True)
    amount_vat_payable = fields.Float('VAT Payable', compute='_compute_price', store=True, readonly=True, copy=False)

    @api.onchange('vat_id')
    def onchange_vat_id(self):
        if self.vat_id.id:
            self.invoice_line_tax_ids -= self.invoice_line_tax_ids.filtered(lambda x: x.is_vat is True)
            self.invoice_line_tax_ids += self.vat_id
        else:
            self.invoice_line_tax_ids -= self.invoice_line_tax_ids.filtered(lambda x: x.is_vat is True)

    @api.onchange('tds_id')
    def onchange_tds_id(self):
        if self.tds_id.id:
            self.invoice_line_tax_ids -= self.invoice_line_tax_ids.filtered(lambda x: x.is_tds is True)
            self.invoice_line_tax_ids += self.tds_id
        else:
            self.invoice_line_tax_ids -= self.invoice_line_tax_ids.filtered(lambda x: x.is_tds is True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine, self)._onchange_product_id()

        self.invoice_line_tax_ids = False
        if self.vat_id.id:
            self.invoice_line_tax_ids += self.vat_id
        if self.tds_id.id:
            self.invoice_line_tax_ids += self.tds_id

        return res

    @api.multi
    def _calculate_tds_value(self):
        tds_amount = 0
        base_val = self.quantity * self.price_unit if self.tds_id.effect_base_price else self.price_subtotal

        if self.tds_id.amount_type != 'slab':
            if self.tds_id.price_include:
                tds_amount = base_val - (base_val / (1 + self.tds_id.amount / 100))
            elif self.tds_id.price_exclude:
                tds_amount = (base_val / (1 - self.tds_id.amount / 100)) - base_val
            else:
                tds_amount = base_val * self.tds_id.amount / 100

        return tds_amount


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _convert_prepared_anglosaxon_line(self, line, partner):
        res = super(ProductProduct, self)._convert_prepared_anglosaxon_line(line, partner)
        if res:
            if line.get('is_tdsvat_payable'):
                res.update({'is_tdsvat_payable': line.get('is_tdsvat_payable'), 'tax_type': line.get('tax_type')})
        return res
