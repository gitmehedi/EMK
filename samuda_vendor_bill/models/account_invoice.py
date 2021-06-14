from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = ['account.invoice', 'ir.needaction_mixin']

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit',
                                        default=lambda self: self.env['res.users'].operating_unit_default_get(self._uid),
                                        readonly=True, required=True, states={'draft': [('readonly', False)]})
    provisional_expense = fields.Boolean(default=False, string='Is Provisional Expense', track_visibility='onchange',
                                         readonly=True, states={'draft': [('readonly', False)]},
                                         help="To manage provisional expense")

    def _prepare_tax_line_vals(self, line, tax):
        vals = super(AccountInvoice, self)._prepare_tax_line_vals(line, tax)
        if vals:
            tax_obj = self.env['account.tax'].browse(tax['id'])
            vals['is_vat'] = tax_obj.is_vat or False
            vals['product_id'] = line.product_id.id
            vals['operating_unit_id'] = line.operating_unit_id.id

        return vals

    @api.model
    def tax_line_move_line_get(self):
        res = super(AccountInvoice, self).tax_line_move_line_get()
        new_res = []
        for r in res:
            invoice_tax_line = self.env['account.invoice.tax'].search([('id', '=', r['invoice_tax_line_id'])])
            operating_unit_id = invoice_tax_line.operating_unit_id.id or self.operating_unit_id.id
            r['operating_unit_id'] = operating_unit_id

            if not r['tax_line_id']:
                tax_amount = r['price']
                r['price'] = r['price_unit'] = (tax_amount * -1)
                r['tax_type'] = 'vat' if invoice_tax_line.is_vat else 'tds'
                r['is_tdsvat_payable'] = self.type in ('out_invoice', 'in_invoice') and True
                new_res.append(r)
            else:
                new_res.append(r)

        return new_res

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

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'draft')]


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

        self.price_subtotal = price_subtotal_signed = self.get_price_subtotal(taxes) if taxes else self.quantity * price
        self.price_tax = self.get_price_tax(taxes) if taxes else 0.0
        self.price_total = taxes['total_included'] if taxes else self.quantity * price
        if self.invoice_id.currency_id and self.invoice_id.company_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(
                date=self.invoice_id._get_currency_rate_date()).compute(price_subtotal_signed,
                                                                        self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign

    @api.multi
    def get_price_subtotal(self, taxes):
        price_subtotal = taxes['total_excluded']
        if self.vat_id.amount_type == 'group':
            tax_ids = list(map(lambda t: t['id'], taxes['taxes']))
            account_tax_pools = self.env['account.tax'].browse(tax_ids)
            if all(tax.price_include for tax in account_tax_pools):
                price_subtotal = taxes['taxes'][0]['base']

        return price_subtotal


class AccountInvoiceTax(models.Model):
    _inherit = 'account.invoice.tax'

    operating_unit_id = fields.Many2one('operating.unit', string='Branch')
    product_id = fields.Many2one('product.product', string='Product')
    is_vat = fields.Boolean(string='Is VAT', default=True)

    @api.constrains('amount')
    def _check_amount(self):
        if self.amount < 0:
            raise ValidationError(_("The amount of Tax can not be negative!!!"))
