import math
from odoo import models, fields, api, _

class AccountTax(models.Model):
    _inherit = 'account.tax'


    def _compute_amount_for_mushok(self, base_amount, price_unit, quantity=1.0, product=None, partner=None,vat_selection=None):
        """ Returns the amount of a single tax for mushok 11. base_amount is the actual amount on which the tax is applied, which is
            price_unit * quantity eventually affected by previous taxes (if tax is include_base_amount XOR price_include)
        """
        self.ensure_one()

        if vat_selection == 'mushok':
            vat_amount = self.mushok_amount
        elif vat_selection == 'vds_authority':
            vat_amount = self.vds_amount
        else:
            vat_amount = 0.0

        if self.amount_type == 'fixed':
            if base_amount:
                return math.copysign(quantity, base_amount) * vat_amount
            else:
                return quantity * vat_amount
        if (self.amount_type == 'percent' and not self.price_include) or (self.amount_type == 'division' and self.price_include):
            return base_amount * vat_amount / 100
        if self.amount_type == 'percent' and self.price_include:
            return base_amount - (base_amount / (1 + vat_amount / 100))
        if self.amount_type == 'division' and not self.price_include:
            return base_amount / (1 - vat_amount / 100) - base_amount

    @api.multi
    def compute_all_for_mushok(self, price_unit, currency=None, quantity=1.0, product=None, partner=None,vat_selection=None):
        """ This method only for mushok 11 calculation.
            This method considered price include and exclude.
         """
        if len(self) == 0:
            company_id = self.env.user.company_id
        else:
            company_id = self[0].company_id
        if not currency:
            currency = company_id.currency_id
        taxes = []
        prec = currency.decimal_places

        round_tax = False if company_id.tax_calculation_rounding_method == 'round_globally' else True
        round_total = True
        if 'round' in self.env.context:
            round_tax = bool(self.env.context['round'])
            round_total = bool(self.env.context['round'])

        if not round_tax:
            prec += 5

        base_values = self.env.context.get('base_values')
        if not base_values:
            total_excluded = total_included = base = round(price_unit * quantity, prec)
        else:
            total_excluded, total_included, base = base_values

        for tax in self.sorted(key=lambda r: r.sequence):
            if tax.amount_type == 'group':
                children = tax.children_tax_ids.with_context(base_values=(total_excluded, total_included, base))
                ret = children.compute_all(price_unit, currency, quantity, product, partner)
                total_excluded = ret['total_excluded']
                base = ret['base'] if tax.include_base_amount else base
                total_included = ret['total_included']
                tax_amount = total_included - total_excluded
                taxes += ret['taxes']
                continue

            tax_amount = tax._compute_amount_for_mushok(base, price_unit, quantity, product, partner,vat_selection)
            if not round_tax:
                tax_amount = round(tax_amount, prec)
            else:
                tax_amount = currency.round(tax_amount)

            if tax.price_include:
                total_excluded -= tax_amount
                base -= tax_amount
            else:
                total_included += tax_amount

            # Keep base amount used for the current tax
            tax_base = base

            if tax.include_base_amount:
                base += tax_amount

            taxes.append({
                'id': tax.id,
                'name': tax.with_context(**{'lang': partner.lang} if partner else {}).name,
                'amount': tax_amount,
                'base': tax_base,
                'sequence': tax.sequence,
                'account_id': tax.account_id.id,
                'refund_account_id': tax.refund_account_id.id,
                'analytic': tax.analytic,
            })

        return {
            'taxes': sorted(taxes, key=lambda k: k['sequence']),
            'total_excluded': currency.round(total_excluded) if round_total else total_excluded,
            'total_included': currency.round(total_included) if round_total else total_included,
            'base': base,
        }