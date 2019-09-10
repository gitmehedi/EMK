from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class InheritAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    conversion_rate = fields.Float(string='Conversion Rate')

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        res = super(InheritAccountInvoice, self)._onchange_currency_id()
        if self.currency_id:
            to_currency = self.company_id.currency_id
            from_currency = self.currency_id.with_context(
                date=self._get_currency_rate_date() or fields.Date.context_today(self))
            self.conversion_rate = to_currency.round(to_currency.rate / from_currency.rate)
        return res

    @api.model
    def create(self, vals):
        if not vals.get('conversion_rate'):
            currency = self.env['res.currency'].search([('id','=',vals.get('currency_id'))])
            to_currency = self.env.user.company_id.currency_id
            from_currency = currency.with_context(
                date=fields.Date.context_today(self))
            vals['conversion_rate'] = to_currency.round(to_currency.rate / from_currency.rate)
        res = super(InheritAccountInvoice, self).create(vals)
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
        if self.currency_id.id != self.company_id.currency_id.id and self.conversion_rate < 60:
            raise ValidationError(_("Give the proper conversion rate."))

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
