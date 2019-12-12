from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = ['account.invoice', 'ir.needaction_mixin']
    _order = 'number DESC, id desc'

    entity_service_id = fields.Many2one('product.product', string='Product/Service', readonly=True,
                                        states={'draft': [('readonly', False)]}, track_visibility='onchange')
    operating_unit_id = fields.Many2one('operating.unit', 'Branch',
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid),
                                        readonly=True, required=True,
                                        states={'draft': [('readonly', False)]})
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', 'Sub Operating Unit',
                                            readonly=True, states={'draft': [('readonly', False)]})
    payment_line_ids = fields.One2many('payment.instruction', 'invoice_id', string='Payment')
    security_deposit = fields.Float('Security Deposit', track_visibility='onchange', copy=False,
                                    readonly=True, states={'draft': [('readonly', False)]})
    security_deposit_account_id = fields.Many2one('account.account', string='Security Deposit Account',
                                                  default=lambda
                                                      self: self.env.user.company_id.security_deposit_account_id.id,
                                                  required=True, readonly=True, states={'draft': [('readonly', False)]})
    total_payment_amount = fields.Float('Total Payment', compute='_compute_payment_amount',
                                        store=True, readonly=True, track_visibility='onchange', copy=False)
    total_payment_approved = fields.Float('Approved Payment', compute='_compute_payment_amount',
                                          store=True, readonly=True, track_visibility='onchange', copy=False)
    vat_selection = fields.Selection([('normal', 'General'),
                                      ('mushok', 'Mushok-6.3'),
                                      ('vds_authority', 'VDS Authority'),
                                      ], string='VAT Selection', default='normal',
                                     readonly=True, states={'draft': [('readonly', False)]})
    payment_approver = fields.Text('Payment Instruction Responsible', track_visibility='onchange',
                                   help="Log for payment approver", copy=False)
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
    date_invoice = fields.Date(default=fields.Datetime.now,states={'draft': [('readonly', True)]})
    total_bill_payable = fields.Float(string='Bill Payable', compute='_computer_bill_payable',store=True)
    vendor_account_id = fields.Many2one('account.account',string='Account', related='partner_id.property_account_payable_id',store=True)

    @api.one
    @api.depends('residual','total_payment_amount','total_payment_approved')
    def _computer_bill_payable(self):
        self.total_bill_payable = self.residual + self.total_payment_approved

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
    @api.depends('payment_line_ids.amount', 'payment_line_ids.state')
    def _compute_payment_amount(self):
        for invoice in self:
            invoice.total_payment_amount = sum(
                line.amount for line in invoice.payment_line_ids if line.state not in ['cancel'])
            invoice.total_payment_approved = sum(
                line.amount for line in invoice.payment_line_ids if line.state in ['approved'])

    @api.one
    @api.depends('amount_untaxed', 'amount_tax', 'vat_selection')
    def _compute_total_amount_with_vat(self):
        for invoice in self:
            if invoice.amount_untaxed and invoice.amount_tax:
                invoice.total_amount_with_vat = invoice.amount_untaxed + invoice.amount_tax

    @api.onchange("reference")
    def onchange_strips(self):
        if self.reference:
            self.reference = self.reference.strip()

    @api.onchange("entity_service_id")
    def onchange_entity_service_id(self):
        self.partner_id = []
        if self.entity_service_id:
            domain = {'partner_id': [('entity_services', 'in', self.entity_service_id.id)]}
        else:
            domain = {'partner_id': [('supplier', '=', True)]}
        return {
            'domain': domain
        }

    @api.constrains('reference')
    def _check_unique_reference(self):
        if self.partner_id and self.reference:
            filters = [['reference', '=ilike', self.reference], ['partner_id', '=', self.partner_id.id],
                       ['state', '!=', 'cancel']]
            bill_no = self.search(filters)
            if len(bill_no) > 1:
                raise UserError(_('Reference must be unique for %s !') % self.partner_id.name)

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
                    {'product_id': line.product_id.id, 'name': line.name, 'mushok_vds_amount': line.mushok_vds_amount})
            else:
                res.update({'product_id': line.product_id.id, 'name': line.name})
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

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        if self.security_deposit > 0.0:
            for line in move_lines:
                if line[2]['name'] == '/':
                    line[2]['credit'] = line[2]['credit'] - self.security_deposit
            if self.env.user.company_id.head_branch_id:
                branch_id = self.env.user.company_id.head_branch_id.id
            else:
                branch_id = self.operating_unit_id.id
            security_deposit_values = {
                'account_id': self.security_deposit_account_id.id,
                # 'analytic_account_id': self.invoice_line_ids[0].account_analytic_id.id,
                'credit': self.security_deposit,
                'date_maturity': self.date_due,
                'debit': False,
                'invoice_id': self.id,
                'name': self.invoice_line_ids[0].name,
                'operating_unit_id': branch_id,
                'partner_id': self.partner_id.id,
            }
            move_lines.append((0, 0, security_deposit_values))
        return move_lines

    @api.multi
    def action_invoice_open(self):
        if self.state == 'draft':
            if self.env.user.id == self.user_id.id and self.env.user.id != SUPERUSER_ID:
                raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))
            return super(AccountInvoice, self).action_invoice_open()
        else:
            raise ValidationError(_("[Validation Error] Vendor Bill {} already validated.".format(self.number)))

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
                    account_move_line.write({'name': self.invoice_line_ids[0].name})
        return res

    @api.multi
    def do_merge(self, keep_references=True, date_invoice=False):
        for invoice in self:
            invoice.reference = ''
        res = super(AccountInvoice, self).do_merge(keep_references=keep_references, date_invoice=date_invoice)
        if res:
            self.browse(res).write({'merged_bill': True})
        return res

    def action_payment_instruction(self):
        if self.residual <= 0.0:
            raise ValidationError(_('There is no remaining balance for this Bill!'))

        if self.residual <= sum(line.amount for line in self.payment_line_ids if line.state == 'draft'):
            raise ValidationError(_('Without Approval/Rejection of previous payment instruction'
                                    ' no new payment instruction can possible!'))

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
            'context': {
                'invoice_amount': (self.residual + self.total_payment_approved) - self.total_payment_amount or 0.0,
                'currency_id': self.currency_id.id or False,
                'op_unit': self.operating_unit_id.id or False,
                'partner_id': self.partner_id.id or False,
                'sub_op_unit': self.invoice_line_ids[0].sub_operating_unit_id.id if self.invoice_line_ids[
                    0].sub_operating_unit_id else None,
            }
        }

    def action_paid_invoice(self):
        to_pay_invoices = self.search([('state', '=', 'open')]).filtered(lambda inv: len(inv.payment_line_ids) > 0
                                                                                     and inv.residual <= inv.total_payment_amount)
        for to_pay_invoice in to_pay_invoices:
            if len([i.is_sync for i in to_pay_invoice.payment_line_ids if not i.is_sync]) > 0:
                pass
            else:
                for line in to_pay_invoice.suspend_security().move_id.line_ids:
                    if line.account_id.internal_type in ('receivable', 'payable'):
                        line.write({'amount_residual': 0.0})
                to_pay_invoice.write({'state': 'paid'})
        return True

    @api.constrains('date_invoice')
    def _check_date_invoice(self):
        date = fields.Date.today()
        if self.date_invoice:
            if self.date_invoice > date:
                raise ValidationError(
                    "Please Check Bill Date!! \n 'Bill Date' can not be future date")

    @api.model
    def create(self, vals):
        if vals.get('reference'):
            vals['reference'] = vals['reference'].strip()
        return super(AccountInvoice, self).create(vals)

    @api.multi
    def write(self, vals):
        if self.state=='draft':
            if vals.get('reference'):
                vals.update({'reference': vals.get('reference').strip()})
            return super(AccountInvoice, self).write(vals)

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'open')]

    @api.model
    def _get_invoice_line_key_cols(self):
        res = super(AccountInvoice, self)._get_invoice_line_key_cols()
        res.append('operating_unit_id')
        res.append('sub_operating_unit_id')
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
            if self.invoice_id.vat_selection == 'mushok':
                if self.invoice_line_tax_ids[0].mushok_amount > 0.0:
                    self.mushok_vds_amount = taxes['taxes'][0]['amount'] / (
                        self.invoice_line_tax_ids[0].amount / self.invoice_line_tax_ids[0].mushok_amount)
                else:
                    self.mushok_vds_amount = 0
            elif self.invoice_id.vat_selection == 'vds_authority':
                if self.invoice_line_tax_ids[0].vds_amount > 0.0:
                    self.mushok_vds_amount = taxes['taxes'][0]['amount'] / (
                        self.invoice_line_tax_ids[0].amount / self.invoice_line_tax_ids[0].vds_amount)
                else:
                    self.mushok_vds_amount = 0
            else:
                self.mushok_vds_amount = taxes['taxes'][0]['amount']

    price_subtotal = fields.Monetary(string='Amount With Vat',
                                     store=True, readonly=True, compute='_compute_price')
    price_subtotal_without_vat = fields.Monetary(string='Amount',
                                                 store=True, readonly=True, compute='_compute_price')
    operating_unit_id = fields.Many2one('operating.unit', string='Branch', required=True,
                                        related='', readonly=False,
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid))
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Sub Operating Unit')
    quantity = fields.Float(digits=0)
    invoice_line_tax_ids = fields.Many2many(string='VAT')
    mushok_vds_amount = fields.Float('VAT Payable', compute='_compute_price', store=True, readonly=True, copy=False)
    asset_name = fields.Char(string='Asset Name')

    # @api.onchange('operating_unit_id')
    # def _onchange_operating_unit_id(self):
    #     for line in self:
    #         line.sub_operating_unit_id = []
    #         sub_operating_unit_ids = self.env['sub.operating.unit'].search([
    #             ('operating_unit_id', '=', self.operating_unit_id.id)]).ids
    #         return {'domain': {
    #             'sub_operating_unit_id': [('id', 'in', sub_operating_unit_ids)]
    #         }}

    @api.constrains('invoice_line_tax_ids')
    def _check_supplier_taxes_id(self):
        if self.invoice_line_tax_ids and len(self.invoice_line_tax_ids) > 1:
            raise Warning('You can select one VAT!')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        vals = super(AccountInvoiceLine, self)._onchange_product_id()
        self.sub_operating_unit_id = []
        if self.product_id:
            self.asset_name = self.product_id.name
            vals['domain']['sub_operating_unit_id'] = [('product_id', '=', self.product_id.id)]
        return vals


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
                res.update({'is_tdsvat_payable': line.get('is_tdsvat_payable'), 'tax_type': line.get('tax_type')})
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
