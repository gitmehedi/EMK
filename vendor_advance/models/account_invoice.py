from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    advance_ids = fields.Many2many('vendor.advance', 'account_invoice_vendor_advance_rel',
                                   'invoice_id', 'advance_id', required=False, readonly=True, copy=False,
                                   states={'draft': [('readonly', False)]}, string='Advances')
    adjusted_advance = fields.Float('Adjusted Advance Amount', readonly=True,
                                    states={'draft': [('readonly', False)]}, copy=False)
    adjustable_vat = fields.Float('Adjustable Vat', readonly=True, copy=False,
                                  compute='_compute_adjustable_vat_tds', store=True)
    adjusted_vat = fields.Float('Adjusted Vat', readonly=True, cody=False)
    adjustable_tds = fields.Float('Adjustable TDS', readonly=True, copy=False,
                                  compute='_compute_adjustable_vat_tds', store=True)
    adjusted_tds = fields.Float('Adjusted TDS', readonly=True, copy=False)

    @api.onchange('invoice_line_ids', 'adjusted_advance')
    def _onchange_invoice_line_ids(self):
        super(AccountInvoice, self)._onchange_invoice_line_ids()
        return

    @api.onchange('advance_ids')
    def _onchange_advance_ids(self):
        for rec in self:
            if not self.env.context.get('noonchange', False):
                rec.adjusted_advance = sum(advance.outstanding_amount for advance in rec.advance_ids)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        for rec in self:
            rec.advance_ids = None
            rec.adjusted_advance = 0.0
        return res

    @api.one
    @api.depends('adjusted_advance', 'tax_line_ids', 'advance_ids')
    def _compute_adjustable_vat_tds(self):
        remaining = self.adjusted_advance
        adjustable_vat = 0.0
        adjustable_tds = 0.0
        if self.advance_ids:
            for advance in self.advance_ids:
                if remaining > 0:
                    if advance.outstanding_amount <= remaining:
                        adjustable_advance = advance.outstanding_amount
                    elif advance.outstanding_amount > remaining > 0:
                        adjustable_advance = remaining
                    remaining -= adjustable_advance
                    if advance.vat_amount > 0:
                        current_adjustable_vat = adjustable_advance * (
                                    advance.vat_amount / advance.initial_outstanding_amount)
                    else:
                        current_adjustable_vat = 0

                    if advance.tds_amount > 0:
                        current_adjustable_tds = adjustable_advance * (
                                    advance.tds_amount / advance.initial_outstanding_amount)
                    else:
                        current_adjustable_tds = 0

                    adjustable_vat += current_adjustable_vat
                    adjustable_tds += current_adjustable_tds
        total_vat = sum(tax_line.amount for tax_line in self.tax_line_ids if
                        tax_line.tax_id.is_reverse and tax_line.tax_id.is_vat)
        total_tds = sum(tax_line.amount for tax_line in self.tax_line_ids if
                        tax_line.tax_id.is_reverse and tax_line.tax_id.is_tds)

        self.adjustable_vat = adjustable_vat if total_vat > adjustable_vat else total_vat
        self.adjustable_tds = adjustable_tds if total_tds > adjustable_tds else total_tds

    @api.constrains('advance_ids', 'adjusted_advance', 'invoice_line_ids')
    def _check_adjusted_advance(self):
        if self.advance_ids:
            self._check_advance_amount(self.advance_ids, self.adjusted_advance)
        if self.invoice_line_ids and self.adjusted_advance:
            invoice_amount = sum(line.price_subtotal for line in self.invoice_line_ids)
            if self.adjusted_advance > invoice_amount:
                raise ValidationError(
                    _("[Validation Error] Adjusted Advance Amount can not be bigger than Invoice Amount"))

    def _check_advance_amount(self, advance_ids, amount):
        total_outstanding_amount = sum(advance.outstanding_amount for advance in advance_ids)
        outstanding_msg = ''
        if amount > total_outstanding_amount:
            outstanding_msg += "The adjusted advance amount is more than any of the outstanding advances.\
                            Summation of outstanding amount of selected advances is {} \n".format(
                total_outstanding_amount)
            for advance in advance_ids:
                outstanding_msg += "The outstanding amount for '{}' is {} \n".format(advance.name,
                                                                                     advance.outstanding_amount)
            outstanding_msg += "So please change the Adjusted Advance Amount"
            raise ValidationError(outstanding_msg)

    @api.multi
    def action_invoice_open(self):
        if self.advance_ids:
            self._check_advance_amount(self.advance_ids, self.adjusted_advance)
        return super(AccountInvoice, self).action_invoice_open()

    # updating_move_line_if_any_advance_is_adjusted
    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        move_lines = super(AccountInvoice, self).finalize_invoice_move_lines(move_lines)
        if self.advance_ids:
            self.update_move_lines_with_advances(move_lines, self.adjusted_advance)
        return move_lines

    # adjusting_vat_and_tds_for_advance_in_tax_line
    @api.model
    def tax_line_move_line_get(self):
        res = super(AccountInvoice, self).tax_line_move_line_get()
        tax_pool = self.env['account.tax']
        adjustable_vat_remaining = self.adjustable_vat
        adjustable_tds_remaining = self.adjustable_tds
        adjusted_vat = 0.0
        adjusted_tds = 0.0
        if res:
            for r in res:
                if adjustable_vat_remaining > 0 or adjustable_tds_remaining > 0:
                    tax = tax_pool.search([('id', '=', r['tax_line_id'])])[0]
                    tax_amount = r['price']
                    compared_tax_value = abs(tax_amount)
                    if tax.is_vat and tax.is_reverse:
                        if compared_tax_value >= adjustable_vat_remaining:
                            tax_amount = tax_amount + adjustable_vat_remaining
                            adjusted_vat += adjustable_vat_remaining
                            adjustable_vat_remaining = 0.0
                        elif adjustable_vat_remaining > compared_tax_value > 0:
                            adjusted_vat += compared_tax_value
                            adjustable_vat_remaining -= compared_tax_value
                            tax_amount = 0.0

                    elif tax.is_tds and tax.is_reverse:
                        if compared_tax_value >= adjustable_tds_remaining:
                            tax_amount = tax_amount + adjustable_tds_remaining
                            adjusted_tds += adjustable_tds_remaining
                            adjustable_tds_remaining = 0.0
                        elif adjustable_tds_remaining > compared_tax_value > 0:
                            adjusted_tds += compared_tax_value
                            adjustable_tds_remaining -= compared_tax_value
                            tax_amount = 0.0
                    r['price'] = r['price_unit'] = tax_amount

        self.write({'adjusted_vat': adjusted_vat,
                    'adjusted_tds': adjusted_tds})
        return res

    def update_move_lines_with_advances(self, move_lines, amount):
        if amount:
            for line in move_lines:
                if line[2]['account_id'] == self.partner_id.property_account_payable_id.id:
                    credit = line[2]['credit']
                    line[2]['credit'] = round(credit - amount, 3)
            balance = self.adjusted_advance
            for advance in self.advance_ids:
                if balance > 0:
                    advance_values = self.get_advance_line_item(advance)
                    advance_credit_amount = 0
                    adjustable_advance = advance.outstanding_amount
                    if balance >= adjustable_advance:
                        advance_credit_amount = adjustable_advance
                    elif adjustable_advance > balance > 0:
                        advance_credit_amount = balance
                    balance = balance - advance_credit_amount
                    if advance_credit_amount > 0:
                        advance_values['credit'] = advance_credit_amount
                        move_lines.append((0, 0, advance_values))
                        invoice_id = self.id
                        billing_date = self.date_invoice
                        self._update_vendor_advance(advance, invoice_id, advance_credit_amount, billing_date)

        return True

    def get_advance_line_item(self, advance):
        name = advance.name
        if self.invoice_line_ids and self.invoice_line_ids[0].name:
            name = self.invoice_line_ids[0].name
        advance_values = {
            'account_id': advance.account_id.id,
            # 'analytic_account_id': self.invoice_line_ids[0].account_analytic_id.id,
            'date_maturity': self.date_due,
            'debit': 0.0,
            'invoice_id': self.id,
            'name': name,
            'partner_id': self.partner_id.id,
            'advance_id': advance.id
        }
        return advance_values

    def _update_vendor_advance(self, advance, invoice_id, adjusted_amount, billing_date):
        vals = {}
        total_adjustment_amount = advance.adjusted_amount + adjusted_amount
        vals['adjusted_amount'] = total_adjustment_amount
        if advance.initial_outstanding_amount == total_adjustment_amount and advance.type == 'single':
            vals['state'] = 'done'
        advance.write(vals)
        self.env['vendor.bill.line'].create({
            'advance_id': advance.id,
            'invoice_id': invoice_id,
            'adjusted_amount': adjusted_amount,
            'billing_date': billing_date
        })

    def get_remain_tds_amount(self, prev_inv_amount, prev_tds_amount, rec, tds_id):
        if self.advance_ids:
            reduce_adv_amount = 0
            inv_adj_amount = self.adjusted_advance
            for adv in self.advance_ids:
                if adv.outstanding_amount < inv_adj_amount:
                    inv_adj_amount -= adv.outstanding_amount
                    if adv.tds_id.amount_type == 'slab':
                        reduce_adv_amount += adv.outstanding_amount
                else:
                    if adv.tds_id.amount_type == 'slab':
                        reduce_adv_amount += inv_adj_amount
                    inv_adj_amount = 0

            invoice_amount = rec['inv_amount'] - reduce_adv_amount + prev_inv_amount
            slab_rate = self.get_slab_rate(tds_id, invoice_amount)
            cal_tds_amount = (invoice_amount + reduce_adv_amount) * (slab_rate / 100)
            remain_tds_amount = cal_tds_amount - prev_tds_amount
        else:
            total_inv_amount = prev_inv_amount + rec['inv_amount']
            slab_rate = self.get_slab_rate(tds_id, total_inv_amount)
            curr_tds_amount = total_inv_amount * (slab_rate / 100)
            remain_tds_amount = curr_tds_amount - prev_tds_amount

        return round(remain_tds_amount, 2)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    advance_id = fields.Many2one('vendor.advance', required=False)
