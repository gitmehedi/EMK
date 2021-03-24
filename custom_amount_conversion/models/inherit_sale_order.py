from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _prepare_invoice(self):
        """Override _prepare_invoice to set conversion_rate"""
        res = super(SaleOrder, self)._prepare_invoice()

        if self.currency_id:
            to_currency = self.company_id.currency_id
            from_currency = self.currency_id.with_context(date=fields.Date.context_today(self))
            res['conversion_rate'] = to_currency.round(to_currency.rate / from_currency.rate)

        return res
