from odoo import models, fields, api


class InheritAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # This should be a computed field so that value won't store to DB.
    # This value will have to fetch from Sale Order section

    # @api.multi
    # @api.depends('currency_id')
    # def _get_default_conversion_rate(self):
    #     if self.conversion_rate <= 0:
    #         from_currency = self.currency_id.with_context(date=self._get_currency_rate_date() or fields.Date.context_today(self))
    #         to_currency = self.company_id.currency_id
    #         self.conversion_rate = from_currency._get_conversion_rate(from_currency, to_currency)
    #
    # conversion_rate = fields.Float(string='Conversion Rate', compute='_get_default_conversion_rate', store=True)

    conversion_rate = fields.Float(string='Conversion Rate')


    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        res = super(InheritAccountInvoice, self)._onchange_currency_id()
        if self.currency_id:
            to_currency = self.company_id.currency_id
            from_currency = self.currency_id.with_context(
                date=self._get_currency_rate_date() or fields.Date.context_today(self))
            self.conversion_rate = to_currency.rate / from_currency.rate
        return res


    @api.depends('currency_id')
    def _get_fields_invisible(self):
        if self.currency_id.id != self.company_id.currency_id.id:
            self.fields_invisible = False
        else:
            self.fields_invisible = True

    fields_invisible = fields.Boolean(compute='_get_fields_invisible', store=False)

    @api.multi
    def action_invoice_open(self):
        res = super(InheritAccountInvoice, self).action_invoice_open()
        if self.currency_id.id != self.company_id.currency_id.id:
            converted_amount = self.amount_total * self.conversion_rate

            # field of account.invoice
            self.amount_total_company_signed = converted_amount
            self.amount_untaxed_signed = converted_amount
            self.residual_company_signed = converted_amount

            # field of account.invoice.line
            self.invoice_line_ids.price_subtotal_signed = converted_amount

            # field of account.move
            self.move_id.amount = converted_amount

            for aml in self.move_id.line_ids:
                # separate two account move line based on balance
                # set amount_residual, balance, debit if balance is positive
                if aml.balance >= 0:
                    self._cr.execute("""UPDATE      account_move_line
                                        SET         amount_residual=%s, balance=%s, debit=%s
                                        WHERE       id=%s
                                        """, (converted_amount, converted_amount, converted_amount, aml.id))
                else:
                    # set balance, credit if balance is negative
                    self._cr.execute("""UPDATE      account_move_line
                                        SET         balance=%s, credit=%s
                                        WHERE       id=%s
                                        """, (-converted_amount, converted_amount, aml.id))
