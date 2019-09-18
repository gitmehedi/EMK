from odoo import api, fields, models


class InheritCurrency(models.Model):
    _inherit = "res.currency"

    @api.model
    def _get_conversion_rate(self, from_currency, to_currency):
        result = super(InheritCurrency, self)._get_conversion_rate(from_currency, to_currency)
        if 'payment_conversion_rate' in self._context and self._context.get('payment_conversion_rate'):
            result = self._context.get('payment_conversion_rate')

        return result
