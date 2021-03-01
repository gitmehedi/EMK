from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class InheritAccountPayment(models.Model):
    _inherit = 'account.payment'

    conversion_rate = fields.Float(string='Conversion Rate')
    conversion_rate_visibility = fields.Boolean(compute='_compute_fields_visibility')

    @api.depends('currency_id')
    def _compute_fields_visibility(self):
        for rec in self:
            rec.conversion_rate_visibility = True if rec.company_id.currency_id.id and \
                                                     rec.currency_id.id != rec.company_id.currency_id.id else False

    @api.onchange('currency_id', 'journal_id')
    def _onchange_currency_id(self):
        if self.currency_id.id and self.company_id.currency_id.id:
            to_currency = self.company_id.currency_id
            from_currency = self.currency_id.with_context(date=fields.Date.context_today(self))
            self.conversion_rate = to_currency.round(to_currency.rate / from_currency.rate)

    @api.constrains('conversion_rate')
    def _check_conversion_rate(self):
        if self.currency_id.id != self.company_id.currency_id.id and self.conversion_rate < 60:
            raise ValidationError(_("Give the proper conversion rate."))

    @api.multi
    def post(self):
        # if company currency and customer payment currency are different,
        # conversion_rate will be passed with context.
        rec = self.with_context(payment_conversion_rate=self.conversion_rate) \
            if self.currency_id.id != self.company_id.currency_id.id else self
        result = super(InheritAccountPayment, rec).post()
        return result
