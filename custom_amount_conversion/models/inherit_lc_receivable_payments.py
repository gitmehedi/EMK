from odoo import api, fields, models, _


class LCReceivablePayment(models.Model):
    _inherit = 'lc.receivable.payment'

    @api.multi
    @api.depends('lc_id', 'date', 'invoice_ids')
    def _compute_rate_amounts(self):
        # do base operation
        super(LCReceivablePayment, self)._compute_rate_amounts()

        # Calculate Base Amount using conversion rate
        for rec in self:
            if rec.lc_id and rec.invoice_ids:
                rec.currency_rate = rec.invoice_ids[0].conversion_rate
                rec.amount_in_company_currency = sum(inv.residual * inv.conversion_rate for inv in rec.invoice_ids)