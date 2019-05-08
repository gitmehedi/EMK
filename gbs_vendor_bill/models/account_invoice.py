# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = ['account.invoice','ir.needaction_mixin']

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice',
                 'type')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal_without_vat for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount) for line in self.tax_line_ids if line.tax_id)
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

    @api.one
    @api.depends('payment_line_ids.amount')
    def _compute_payment_amount(self):
        for invoice in self:
            invoice.total_payment_amount = sum(line.amount for line in invoice.payment_line_ids)

    operating_unit_id = fields.Many2one('operating.unit', 'Branch',
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid),
                                        readonly=True,required=True,
                                        states={'draft': [('readonly',False)]})
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', 'Sub Operating Unit',
                                            readonly=True,states={'draft': [('readonly',False)]})

    payment_line_ids = fields.One2many('payment.instruction', 'invoice_id', string='Payment')
    total_payment_amount = fields.Float('Total Payment', compute='_compute_payment_amount',
                                        store=True, readonly=True, track_visibility='onchange',copy=False)

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):
        for invoice in self:
            invoice.sub_operating_unit_id = []

    @api.constrains('reference')
    def _check_unique_reference(self):
        if self.partner_id and self.reference:
            filters = [['reference', '=ilike', self.reference],['partner_id', '=', self.partner_id.id],['state','!=','cancel']]
            bill_no = self.search(filters)
            if len(bill_no) > 1:
                raise UserError(_('Reference must be unique for %s !') % self.partner_id.name)


    @api.model
    def invoice_line_move_line_get(self):
        res = super(AccountInvoice, self).invoice_line_move_line_get()
        if res:
            for iml in res:
                inv_line_obj = self.env['account.invoice.line'].search([('id','=',iml['invl_id'])])
                iml.update({'operating_unit_id': inv_line_obj.operating_unit_id.id})
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
                    'operating_unit_id': tax_line.operating_unit_id.id,
                    'tax_ids': [(6, 0, list(done_taxes))] if tax_line.tax_id.include_base_amount else []
                })
                done_taxes.append(tax.id)
        return res

    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        for line in self.invoice_line_ids:
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id,
                                                          self.partner_id)['taxes']
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)

                val.update({'operating_unit_id': line.operating_unit_id.id})
                key = key+'-'+str(line.operating_unit_id.id)
                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
        return tax_grouped

    # @api.multi
    # def finalize_invoice_move_lines(self, move_lines):
    #     return move_lines

    @api.multi
    def action_move_create(self):
        res = super(AccountInvoice, self).action_move_create()
        if res:
            for inv in self:
                account_move = self.env['account.move'].search([('id','=',inv.move_id.id)])
                account_move.write({'operating_unit_id': inv.operating_unit_id.id})
        return res

    @api.multi
    def do_merge(self, keep_references=True, date_invoice=False):
        for invoice in self:
            invoice.reference = ''
        return super(AccountInvoice, self).do_merge(keep_references=keep_references, date_invoice=date_invoice)

    def action_payment_instruction(self):
        if self.residual <= 0.0:
            raise ValidationError(_('There is no remaining balance for this Bill!'))

        res = self.env.ref('gbs_vendor_bill.view_bill_payment_instruction_wizard')

        return {
            'name': _('Payment Instruction'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'bill.payment.instruction.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {'invoice_amount': self.residual or False,
                        'currency_id': self.currency_id.id or False,
                        },
        }

    def action_paid_invoice(self):
        to_pay_invoices = self.search([('state', '=', 'open')]).filtered(lambda inv: len(inv.payment_line_ids) > 0
                                                               and inv.residual<=inv.total_payment_amount)
        for to_pay_invoice in to_pay_invoices:
            if len([i.is_sync for i in to_pay_invoice.payment_line_ids if not i.is_sync])>0:
                pass
            else:
                for line in to_pay_invoice.suspend_security().move_id.line_ids:
                    if line.account_id.internal_type in ('receivable', 'payable'):
                        line.write({'amount_residual': 0.0})
                to_pay_invoice.write({'state': 'paid'})
        return True

    @api.model
    def create(self, vals):
        if vals.get('reference'):
            vals['reference'] = vals['reference'].strip()
        return super(AccountInvoice, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('reference'):
            vals.update({'reference': vals.get('reference').strip()})
        return super(AccountInvoice, self).write(vals)

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'open')]


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
                                        related='',
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid))
    sub_operating_unit_id = fields.Many2one('sub.operating.unit',string='Sub Operating Unit')

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):
        for line in self:
            line.sub_operating_unit_id = []


class AccountInvoiceTax(models.Model):
    _inherit = "account.invoice.tax"

    operating_unit_id = fields.Many2one('operating.unit', string='Branch')


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
                    move.write({'operating_unit_id':op_unit[0]})
        return res

