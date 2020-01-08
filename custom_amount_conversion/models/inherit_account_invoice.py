from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    conversion_rate = fields.Float(string='Conversion Rate')

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        res = super(AccountInvoice, self)._onchange_currency_id()
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
        res = super(AccountInvoice, self).create(vals)
        return res

    @api.depends('currency_id')
    def _get_fields_invisible(self):
        for rec in self:
            if rec.currency_id.id != rec.company_id.currency_id.id:
                rec.fields_invisible = False
            else:
                rec.fields_invisible = True

    fields_invisible = fields.Boolean(compute='_get_fields_invisible', store=False)

    @api.multi
    def action_invoice_open(self):
        if self.currency_id.id != self.company_id.currency_id.id and self.conversion_rate < 60:
            raise ValidationError(_("Give the proper conversion rate."))

        rec = self.with_context(payment_conversion_rate=self.conversion_rate) \
            if self.currency_id.id != self.company_id.currency_id.id else self

        res = super(AccountInvoice, rec).action_invoice_open()

        return res
