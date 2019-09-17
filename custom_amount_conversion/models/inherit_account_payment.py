from odoo import api, fields, models


class InheritAccountPayment(models.Model):
    _inherit = 'account.payment'

    conversion_rate = fields.Float(string='Conversion Rate')
    hide_conversion_rate_field = fields.Boolean(compute='_compute_hide_conversion_rate_field', store=False)

    @api.depends('currency_id')
    def _compute_hide_conversion_rate_field(self):
        for rec in self:
            if rec.company_id.currency_id.id and rec.currency_id.id != rec.company_id.currency_id.id:
                rec.hide_conversion_rate_field = False
            else:
                rec.hide_conversion_rate_field = True

    @api.onchange('currency_id', 'journal_id')
    def _onchange_currency_id(self):
        for rec in self:
            if rec.currency_id.id and rec.company_id.currency_id.id:
                to_currency = rec.company_id.currency_id
                from_currency = rec.currency_id.with_context(date=fields.Date.context_today(rec))
                rec.conversion_rate = to_currency.round(to_currency.rate / from_currency.rate)

    @api.multi
    def post(self):
        result = super(InheritAccountPayment, self.with_context(payment_conversion_rate=self.conversion_rate)).post()
        return result
