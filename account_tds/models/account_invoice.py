from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice',
                 'type')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount) for line in self.tax_line_ids if not line.tds_id)
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
    @api.depends('invoice_line_ids.tds_amount')
    def _compute_total_tds(self):
        for invoice in self:
            invoice.total_tds_amount = sum(line.tds_amount for line in invoice.invoice_line_ids)

    is_tds_applicable = fields.Boolean(string='TDS Applicable',default=True,
        readonly=True,states={'draft': [('readonly', False)]},
        help="""TDS applicable/not applicable for this bill.
               If its not applicable then need to take decision 
               that is it for permanent or temporary.""")
    inapplicable_type = fields.Selection([
        ('temporary_inapplicable', 'Temporary'),
        ('permanent_inapplicable', 'Permanent')], string='Select Type',
        readonly=True, states={'draft': [('readonly', False)]},
        help="""If TDS not apply for this bill or supplier already give the TDS for this bill then it will permanently inapplicable.
        If there any chance to add TDS in this bill then its temporary inapplicable""")

    total_tds_amount = fields.Float('Total TDS', compute='_compute_total_tds',
        store=True, readonly=True, track_visibility='always')

    @api.multi
    def action_invoice_open(self):
        if self.is_tds_applicable:
            self._update_tds()
            self._update_tax_line_vals()
        return super(AccountInvoice, self).action_invoice_open()

    def _update_tds(self):
        if not self.date:
            self.date = fields.Date.context_today(self)
        date_range_objs = self.env['date.range'].search(
            [('date_start', '<=', self.date), ('date_end', '>=', self.date), ('type_id.tds_year', '=', True)],
            order='id DESC', limit=1)
        if date_range_objs:
            invoice_objs = self.search(
                [('id', '!=', self.id), ('partner_id', '=', self.partner_id.id), ('is_tds_applicable', '=', True),
                 ('date', '>=', date_range_objs.date_start), ('date', '<=', date_range_objs.date_end)])
            for line in self.invoice_line_ids:
                if invoice_objs:
                    pre_invoice_line_list = []
                    for invoice_obj in invoice_objs:
                        for invoice_line_obj in invoice_obj.invoice_line_ids:
                            if invoice_line_obj.product_id.id == line.product_id.id and invoice_line_obj.account_tds_id.id == line.account_tds_id.id:
                                pre_invoice_line_list.append(invoice_line_obj)
                    line._calculate_tds_value(pre_invoice_line_list)
                else:
                    line._calculate_tds_value()
        else:
            pass

    def _update_tax_line_vals(self):
        for line in self.invoice_line_ids:
            vals = {
                'invoice_id': self.id,
                'name': line.account_tds_id.name,
                'tds_id': line.account_tds_id.id,
                'amount': line.tds_amount,
                'manual': False,
                'sequence': 0,
                'account_id': self.type in ('out_invoice', 'in_invoice') and (line.account_tds_id.account_id.id)
                # 'base': tax['base'],
                # 'tax_id': line.account_tds_id.id,
                # 'account_analytic_id': tax['analytic'] and line.account_analytic_id.id or False,
            }
            self.env['account.invoice.tax'].create(vals)

        return True

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    tds_amount = fields.Float('Tds value',readonly=True,store=True)
    account_tds_id = fields.Many2one('tds.rule',related='product_id.account_tds_id', string='TDS Rule',
                                     store=True)

    @api.multi
    def _calculate_tds_value(self,pre_invoice_line_list=None):
        # for line in self:
        if self.invoice_id.is_tds_applicable and self.product_id:
            pro_base_val = self.quantity * self.price_unit
            if self.account_tds_id.type_rate == 'flat':
                self.tds_amount = pro_base_val * self.account_tds_id.flat_rate/100
                if pre_invoice_line_list:
                    remaining_pre_tds = self.previous_tds_value(self.account_tds_id.flat_rate,pre_invoice_line_list)
                    self.tds_amount = self.tds_amount + remaining_pre_tds
            else:
                for tds_slab_rule_obj in self.account_tds_id.line_ids:
                    if pro_base_val>=tds_slab_rule_obj.range_from and pro_base_val<=tds_slab_rule_obj.range_to:
                        self.tds_amount = pro_base_val * tds_slab_rule_obj.rate / 100
                        if pre_invoice_line_list:
                            remaining_pre_tds = self.previous_tds_value(tds_slab_rule_obj.rate,pre_invoice_line_list)
                            self.tds_amount = self.tds_amount + remaining_pre_tds
                        break
                    else:
                        self.tds_amount = 0.0

    def previous_tds_value(self,current_rate,pre_invoice_line_list):
        remain_tds_amount = 0.0
        if pre_invoice_line_list:
            pre_total_tds = pre_total_base_amount = 0.0
            for pre_invoice_line_obj in pre_invoice_line_list:
                pre_total_tds += pre_invoice_line_obj.tds_amount
                pre_total_base_amount += (pre_invoice_line_obj.price_unit * pre_invoice_line_obj.quantity)

            pre_rate = (pre_total_tds * 100)/pre_total_base_amount
            if current_rate > pre_rate:
                remain_tds_amount = ((pre_total_base_amount *current_rate)/100) - pre_total_tds

        return remain_tds_amount


class AccountInvoiceTax(models.Model):
    _inherit = "account.invoice.tax"

    tds_id = fields.Many2one('tds.rule', string='TDS')

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    tax_type = fields.Selection([('vat', 'VAT'),('tds', 'TDS')], string='TDS Type')
    is_deposit = fields.Boolean('Deposit',default=False)