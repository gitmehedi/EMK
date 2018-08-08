from odoo import fields, api, models


class InheritedSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # @api.multi
    # def _prepare_invoice_line(self, qty):
    #     res = {}
    #
    #     result = {
    #         res['currency_id'] : self.order_id.currency_id.id,
    #     }
    #
    #     return super(InheritedSaleOrderLine, self)._prepare_invoice_line(result)
