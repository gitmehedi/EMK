from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
import itertools
from operator import itemgetter


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = ['account.invoice', 'ir.needaction_mixin']

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit',
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid),
                                        readonly=True, required=True,
                                        states={'draft': [('readonly', False)]})
    vat_selection = fields.Selection([('normal', 'General'),
                                      ('mushok', 'Mushok-6.3'),
                                      ('vds_authority', 'VDS Authority'),
                                      ], string='VAT Selection', default='normal',
                                     readonly=True, states={'draft': [('readonly', False)]})
    merged_bill = fields.Boolean(default=False, string='Is Merged Bill', track_visibility='onchange',
                                 readonly=True, states={'draft': [('readonly', False)]},
                                 help="Log for payment approver")
    provisional_expense = fields.Boolean(default=False, string='Is Provisional Expense', track_visibility='onchange',
                                         readonly=True, states={'draft': [('readonly', False)]},
                                         help="To manage provisional expense")
    mushok_vds_amount = fields.Float('VAT Payable', compute='_compute_amount',
                                     store=True, readonly=True, track_visibility='onchange', copy=False)
    total_amount_with_vat = fields.Float('Total', compute='_compute_total_amount_with_vat',
                                        store=True, readonly=True, track_visibility='onchange', copy=False)

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice',
                 'type')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal_without_vat for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount) for line in self.tax_line_ids if line.tax_id)
        self.mushok_vds_amount = sum(round_curr(line.mushok_vds_amount) for line in self.invoice_line_ids)
        if self.vat_selection == 'normal':
            self.amount_total = self.amount_untaxed + self.amount_tax
        else:
            self.amount_total = self.amount_untaxed + self.mushok_vds_amount
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

    @api.one
    @api.depends('amount_untaxed', 'amount_tax','vat_selection')
    def _compute_total_amount_with_vat(self):
        for invoice in self:
            if invoice.amount_untaxed and invoice.amount_tax:
                invoice.total_amount_with_vat = invoice.amount_untaxed + invoice.amount_tax

    @api.model
    def invoice_line_move_line_get(self):
        res = super(AccountInvoice, self).invoice_line_move_line_get()
        if res:
            for iml in res:
                inv_line_obj = self.env['account.invoice.line'].search([('id', '=', iml['invl_id'])])
                iml.update({'operating_unit_id': inv_line_obj.operating_unit_id.id})
        return res

    def _prepare_tax_line_vals(self, line, tax):
        res = super(AccountInvoice, self)._prepare_tax_line_vals(line, tax)
        if res:
            if self.vat_selection in ['mushok', 'vds_authority']:
                res.update(
                    {'product_id': line.product_id.id, 'name': False, 'mushok_vds_amount': line.mushok_vds_amount})
            else:
                res.update({'product_id': line.product_id.id, 'name': False})
        return res

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
                if self.vat_selection in ['mushok', 'vds_authority'] and tax_line.tax_id:
                    amount = tax_line.mushok_vds_amount
                else:
                    amount = tax_line.amount
                if tax_line.tax_id:
                    tax_type = 'vat'
                else:
                    tax_type = 'tds'
                res.append({
                    'invoice_tax_line_id': tax_line.id,
                    'tax_line_id': tax_line.tax_id.id,
                    'type': 'tax',
                    'name': tax_line.name,
                    'price_unit': -amount,
                    'quantity': 1,
                    'price': -amount,
                    'account_id': tax_line.account_id.id,
                    'product_id': tax_line.product_id.id,
                    'account_analytic_id': tax_line.account_analytic_id.id,
                    'invoice_id': self.id,
                    'operating_unit_id': tax_line.operating_unit_id.id,
                    'is_tdsvat_payable': self.type in ('out_invoice', 'in_invoice') and True,
                    'tax_type': tax_type,
                    'tax_ids': [(6, 0, list(done_taxes))] if tax_line.tax_id.include_base_amount else []
                })
                done_taxes.append(tax.id)
        return res

    # @api.multi
    # def action_invoice_open(self):
    #     if self.env.user.id == self.user_id.id and self.env.user.id != SUPERUSER_ID:
    #         raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))
    #     return super(AccountInvoice, self).action_invoice_open()

    @api.multi
    def action_invoice_open(self):
        sorted_inv_line_ids = sorted(self.invoice_line_ids, key=itemgetter('account_id'))
        for key, group in itertools.groupby(sorted_inv_line_ids, key=lambda x: x['account_id']):
            has_narration = False
            for inv_line_id in list(group):
                if inv_line_id.name:
                    has_narration = True

            if not has_narration:
                raise ValidationError(_("Must have narration for an unique account in Bill records."))

        return super(AccountInvoice, self).action_invoice_open()

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        move_lines = super(AccountInvoice, self).finalize_invoice_move_lines(move_lines)
        # check the type of invoice
        if self.type == 'in_invoice':
            dict_obj = {}
            for line_tuple in move_lines:
                account_id = line_tuple[2]['account_id']
                if account_id not in dict_obj.keys():
                    dict_obj[account_id] = line_tuple
                else:
                    if dict_obj[account_id][2]['name'] and line_tuple[2]['name']:
                        dict_obj[account_id][2]['name'] += ', ' + line_tuple[2]['name']
                    elif not dict_obj[account_id][2]['name'] and line_tuple[2]['name']:
                        dict_obj[account_id][2]['name'] = line_tuple[2]['name']
                    else:
                        pass

                    dict_obj[account_id][2]['debit'] += line_tuple[2]['debit']
                    dict_obj[account_id][2]['credit'] += line_tuple[2]['credit']

            move_lines = list(dict_obj.values())

        return move_lines

    @api.multi
    def action_move_create(self):
        res = super(AccountInvoice, self.sudo()).action_move_create()
        if res:
            for inv in self:
                account_move = self.env['account.move'].search([('id', '=', inv.move_id.id)])
                account_move.write({'operating_unit_id': inv.operating_unit_id.id})
                account_move_line = account_move.line_ids.search(
                    [('name', '=', '/'), ('move_id', '=', account_move.id)])
                if account_move_line:
                    name = self.invoice_line_ids.search([('name', '!=', False), ('invoice_id', '=', self.id)])[0].name
                    account_move_line.write({'name': name})
        return res

    @api.multi
    def do_merge(self, keep_references=True, date_invoice=False):
        for invoice in self:
            invoice.reference = ''
        res = super(AccountInvoice, self).do_merge(keep_references=keep_references, date_invoice=date_invoice)
        if res:
            self.browse(res).write({'merged_bill': True})
        return res

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'draft')]

    @api.model
    def _get_invoice_line_key_cols(self):
        res = super(AccountInvoice, self)._get_invoice_line_key_cols()
        res.append('operating_unit_id')
        # res.append('sub_operating_unit_id')
        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
                 'invoice_id.date_invoice', 'invoice_id.date', 'invoice_id.vat_selection')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,
                                                          partner=self.invoice_id.partner_id)
        self.price_subtotal = taxes['total_included'] if taxes else self.quantity * price
        self.price_subtotal_without_vat = price_subtotal_signed = taxes[
            'total_excluded'] if taxes else self.quantity * price
        if self.invoice_id.currency_id and self.invoice_id.company_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(
                date=self.invoice_id._get_currency_rate_date()).compute(price_subtotal_signed,
                                                                        self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign
        if taxes:
            if self.invoice_id.vat_selection == 'mushok' and self.invoice_line_tax_ids[0].mushok_amount > 0.0:
                self.mushok_vds_amount = taxes['taxes'][0]['amount'] / (
                            self.invoice_line_tax_ids[0].amount / self.invoice_line_tax_ids[0].mushok_amount)
            elif self.invoice_id.vat_selection == 'vds_authority' and self.invoice_line_tax_ids[0].vds_amount > 0.0:
                self.mushok_vds_amount = taxes['taxes'][0]['amount'] / (
                            self.invoice_line_tax_ids[0].amount / self.invoice_line_tax_ids[0].vds_amount)
            else:
                self.mushok_vds_amount = False

    name = fields.Text(string='Narration', required=False)
    price_subtotal = fields.Monetary(string='Amount With Vat',
                                     store=True, readonly=True, compute='_compute_price')
    price_subtotal_without_vat = fields.Monetary(string='Amount',
                                                 store=True, readonly=True, compute='_compute_price')
    operating_unit_id = fields.Many2one('operating.unit', string='Branch', required=True,
                                        related='', readonly=False,
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid))
    quantity = fields.Float(digits=0)
    invoice_line_tax_ids = fields.Many2many(string='VAT')
    mushok_vds_amount = fields.Float('VAT Payable', compute='_compute_price',store=True, readonly=True, copy=False)
    narration = fields.Text('Narration')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine, self)._onchange_product_id()
        self.name = False
        return res


class AccountInvoiceTax(models.Model):
    _inherit = "account.invoice.tax"

    operating_unit_id = fields.Many2one('operating.unit', string='Branch')
    product_id = fields.Many2one('product.product', string='Product')
    mushok_vds_amount = fields.Float('VAT Payable', readonly=True, store=True, copy=False)


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _convert_prepared_anglosaxon_line(self, line, partner):
        res = super(ProductProduct, self)._convert_prepared_anglosaxon_line(line, partner)
        if res:
            if line.get('operating_unit_id'):
                res.update({'operating_unit_id': line.get('operating_unit_id')})
            else:
                inv_obj = self.env['account.invoice'].search([('id', '=', line['invoice_id'])])
                res.update({'operating_unit_id': inv_obj.operating_unit_id.id})
            if line.get('is_tdsvat_payable'):
                res.update({'is_tdsvat_payable': line.get('is_tdsvat_payable'),
                            'tax_type': line.get('tax_type'),
                            })
        return res


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def post(self):
        res = super(AccountMove, self).post()
        if res:
            for move in self:
                op_unit = [i.operating_unit_id.id for i in move.line_ids if i.operating_unit_id]
                if op_unit:
                    move.write({'operating_unit_id': op_unit[0]})
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    _order = "date desc, id asc"

    is_tdsvat_payable = fields.Boolean('TDS/VAT Payable', default=False)
    tax_type = fields.Selection([('vat', 'VAT'), ('tds', 'TDS')], string='TAX/VAT')