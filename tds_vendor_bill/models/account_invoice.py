from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round as round


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    is_tds_applicable = fields.Boolean(string='TDS Applicable', default=True,
                                       readonly=True, states={'draft': [('readonly', False)]},
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
                                    store=True, readonly=True, track_visibility='always', copy=False)
    tax_line_ids = fields.One2many('account.invoice.tax', 'invoice_id', string='VAT', oldname='tax_line',
                                   readonly=True, states={'draft': [('readonly', False)]}, copy=False)
    vat_over_tds = fields.Boolean(string='VAT over TDS', default=False,
                                  readonly=True, states={'draft': [('readonly', False)]},
                                  help="""TDS will applicable to base price for this bill. 
                                       VAT will be calculated on TDS+Base price.""")

    @api.one
    @api.depends('invoice_line_ids.account_tds_id','invoice_line_ids.tds_amount',
                 'is_tds_applicable','tax_line_ids.amount')
    def _compute_total_tds(self):
        for invoice in self:
            if invoice.is_tds_applicable:
                invoice.total_tds_amount = sum(line.amount for line in self.tax_line_ids if line.tds_id)

    @api.onchange('is_tds_applicable')
    def _onchange_is_tds_applicable(self):
        if not self.is_tds_applicable and self.tax_line_ids:
            for line in self.invoice_line_ids:
                line.tds_amount = False
                line.account_tds_id = False

    def _update_tds(self):
        if not self.date:
            self.date = fields.Date.context_today(self)
        date_range_objs = self.env['date.range'].search(
            [('date_start', '<=', self.date), ('date_end', '>=', self.date), ('type_id.tds_year', '=', True),
             ('active', '=', True)],
            order='id DESC', limit=1)
        if date_range_objs:
            if isinstance(self.id, models.NewId):
                invoice_objs = self.search(
                    [('partner_id', '=', self.partner_id.id), ('is_tds_applicable', '=', True),
                     ('date', '>=', date_range_objs.date_start), ('date', '<=', date_range_objs.date_end)])
            else:
                invoice_objs = self.search(
                    [('id', '!=', self.id), ('partner_id', '=', self.partner_id.id), ('is_tds_applicable', '=', True),
                     ('date', '>=', date_range_objs.date_start), ('date', '<=', date_range_objs.date_end)])
            for line in self.invoice_line_ids:
                if invoice_objs:
                    pre_invoice_line_list = []
                    for invoice_obj in invoice_objs:
                        for invoice_line_obj in invoice_obj.invoice_line_ids:
                            # if invoice_line_obj.product_id.id == line.product_id.id and invoice_line_obj.account_tds_id.id == line.account_tds_id.id:
                            if invoice_line_obj.account_tds_id.id == line.account_tds_id.id:
                                pre_invoice_line_list.append(invoice_line_obj)
                    line._calculate_tds_value(pre_invoice_line_list)
                else:
                    line._calculate_tds_value()
        else:
            pass

    def _update_tax_line_vals(self,line):
        if line.account_tds_id and self.type in ('out_invoice', 'in_invoice'):
            if line.account_tds_id.operating_unit_id:
                op_unit_id = line.account_tds_id.operating_unit_id.id
            elif self.env.user.company_id.head_branch_id:
                op_unit_id = self.env.user.company_id.head_branch_id.id
            else:
                op_unit_id = line.operating_unit_id.id or False
            vals = {
                'invoice_id': self.id,
                # 'name': line.account_tds_id.name + '/' + line.name,
                # 'name': line.name,
                'name': False,
                'tds_id': line.account_tds_id.id,
                'amount': line.tds_amount,
                'manual': False,
                'sequence': 0,
                'account_id': line.account_tds_id.account_id.id,
                'account_analytic_id': line.account_analytic_id.id or False,
                'operating_unit_id': op_unit_id,
                'product_id': line.product_id.id or False,
                # 'base': tax['base'],
                # 'tax_id': line.account_tds_id.id,
            }
            # self.env['account.invoice.tax'].create(vals)
        return vals

    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        for line in self.invoice_line_ids:
            if line.account_tds_id.effect_on_base:
                tds = line.tds_amount
                price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0) + tds
            else:
                price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity,
                                                          line.product_id, self.partner_id)['taxes']
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)
                if self.env['account.tax'].browse(tax['id']).operating_unit_id:
                    op_unit_id = self.env['account.tax'].browse(tax['id']).operating_unit_id.id
                elif self.env.user.company_id.head_branch_id:
                    op_unit_id = self.env.user.company_id.head_branch_id.id
                else:
                    op_unit_id = line.operating_unit_id.id or False
                val.update({'operating_unit_id': op_unit_id, 'product_id': line.product_id.id})
                key = key + '-' + str(line.operating_unit_id.id) + '-' + str(line.product_id.id)
                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
            if self.is_tds_applicable and line.account_tds_id:
                self._update_tds()
                val = self._update_tax_line_vals(line)
                key = str(line.account_tds_id.id) + '-' + str(line.operating_unit_id.id) + '-' + str(line.product_id.id)
                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    # tax_grouped[key]['base'] += val['base']
        return tax_grouped

    @api.model
    def _get_invoice_line_key_cols(self):
        res = super(AccountInvoice, self)._get_invoice_line_key_cols()
        res.append('account_tds_id')
        res.append('tds_amount')
        return res

    @api.multi
    def do_merge(self, keep_references=True, date_invoice=False):
        res = super(AccountInvoice, self).do_merge(keep_references=keep_references, date_invoice=date_invoice)
        if res:
            self.browse(res)._update_tds()
            # self.browse(res)._update_tax_line_vals()
        return res


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    tds_amount = fields.Float('TDS Value',copy=False)
    account_tds_id = fields.Many2one('tds.rule', string='TDS',
                                     domain="[('active', '=', True),('state', '=','confirm' )]")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.account_tds_id = False
        if self.product_id:
            self.account_tds_id = self.product_id.account_tds_id.id
        return super(AccountInvoiceLine, self)._onchange_product_id()

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id',
                 'invoice_id.company_id', 'invoice_id.date_invoice', 'invoice_id.date',
                 'invoice_id.vat_selection', 'invoice_id.vat_over_tds')
    def _compute_price(self):
        if self.account_tds_id.effect_on_base:
            currency = self.invoice_id and self.invoice_id.currency_id or None
            price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
            tds = self.tds_amount
            price_with_tds = price + tds
            taxes = False
            if self.invoice_line_tax_ids:
                taxes = self.invoice_line_tax_ids.compute_all(price_with_tds, currency, self.quantity, product=self.product_id,
                                                              partner=self.invoice_id.partner_id)
            self.price_subtotal = taxes['total_included'] if taxes else self.quantity * price_with_tds
            self.price_subtotal_without_vat = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price_with_tds

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
        else:
            return super(AccountInvoiceLine, self)._compute_price()

    @api.onchange('account_tds_id','price_subtotal_without_vat','invoice_id.total_tds_amount')
    def _onchange_account_tds_id(self):
        if self.account_tds_id:
            return self.invoice_id._update_tds()

    @api.multi
    def _calculate_tds_value(self, pre_invoice_line_list=None):
        # for line in self:
        if self.invoice_id.is_tds_applicable and self.name:
            if self.account_tds_id.effect_on_base:
                pro_base_val = self.quantity * self.price_unit
            else:
                pro_base_val = self.price_subtotal_without_vat
            if self.account_tds_id.type_rate == 'flat':
                if self.account_tds_id.price_include:
                    self.tds_amount = pro_base_val-(pro_base_val/(1+self.account_tds_id.flat_rate / 100))
                elif self.account_tds_id.price_exclude:
                    self.tds_amount = (pro_base_val / (1 - self.account_tds_id.flat_rate / 100)) - pro_base_val
                else:
                    self.tds_amount = pro_base_val * self.account_tds_id.flat_rate / 100
                if pre_invoice_line_list:
                    remaining_pre_tds = self.previous_tds_value(self.account_tds_id.flat_rate, pre_invoice_line_list)
                    self.tds_amount = self.tds_amount + remaining_pre_tds
            else:
                for tds_slab_rule_obj in self.account_tds_id.line_ids:
                    if not pre_invoice_line_list and pro_base_val >= tds_slab_rule_obj.range_from and pro_base_val <= tds_slab_rule_obj.range_to:
                        self.tds_amount = pro_base_val * tds_slab_rule_obj.rate / 100
                        break
                    elif pre_invoice_line_list:
                        total_amount = pro_base_val + sum(int(i.price_subtotal_without_vat) for i in pre_invoice_line_list)
                        if total_amount >= tds_slab_rule_obj.range_from and total_amount <= tds_slab_rule_obj.range_to:
                            total_tds_amount = total_amount * tds_slab_rule_obj.rate / 100
                            remaining_tds_amount = total_tds_amount - sum(int(i.tds_amount) for i in pre_invoice_line_list)
                            self.tds_amount = remaining_tds_amount
                            break
                    else:
                        self.tds_amount = 0.0
        return self.tds_amount

    def previous_tds_value(self, current_rate, pre_invoice_line_list):
        remain_tds_amount = 0.0
        if pre_invoice_line_list:
            pre_total_tds = pre_total_base_amount = 0.0
            for pre_invoice_line_obj in pre_invoice_line_list:
                pre_total_tds += pre_invoice_line_obj.tds_amount
                # pre_total_base_amount += (pre_invoice_line_obj.price_unit * pre_invoice_line_obj.quantity)
                if pre_invoice_line_obj.account_tds_id.price_include:
                    pre_total_base_amount += (pre_invoice_line_obj.price_subtotal_without_vat-(pre_invoice_line_obj.price_subtotal_without_vat*(self.account_tds_id.flat_rate / 100)))
                else:
                    pre_total_base_amount += (pre_invoice_line_obj.price_subtotal_without_vat)
            pre_rate = (pre_total_tds * 100) / pre_total_base_amount
            if current_rate > round(pre_rate,False):
                remain_tds_amount = ((pre_total_base_amount * current_rate) / 100) - pre_total_tds
        return remain_tds_amount


class AccountInvoiceTax(models.Model):
    _inherit = "account.invoice.tax"

    tds_id = fields.Many2one('tds.rule', string='TDS')