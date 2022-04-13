from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    service_charge = fields.Float(string='Service Charge')


class PosOrder(models.Model):
    _inherit = 'pos.order'

    service_charge = fields.Float(compute='_compute_amount_all', string='Service Charge', store=True, digits=0)
    amount_tax = fields.Float(compute='_compute_amount_all', string='VAT', digits=0)

    @api.depends('statement_ids', 'lines.price_subtotal_incl', 'lines.discount')
    def _compute_amount_all(self):
        for order in self:
            order.amount_paid = order.amount_return = order.amount_tax = 0.0
            currency = order.pricelist_id.currency_id
            order.amount_paid = sum(payment.amount for payment in order.statement_ids)
            order.amount_return = sum(payment.amount < 0 and payment.amount or 0 for payment in order.statement_ids)
            order.amount_tax = currency.round(
                sum(self._amount_line_tax(line, order.fiscal_position_id) for line in order.lines))
            amount_untaxed = currency.round(sum(line.price_subtotal for line in order.lines))
            service = round(amount_untaxed * (order.session_id.config_id.service_charge / 100))
            order.service_charge = service
            order.amount_total = order.amount_tax + amount_untaxed + service
