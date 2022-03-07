from odoo import api, fields, models, _


class SaleOrderCreditLimitCrossMessageWizard(models.TransientModel):
    _name = 'sale.order.credit.limit.cross.wizard'

    zero_credit_limit = fields.Boolean()

    customer_credit_limit = fields.Char(string="Credit Limit")
    limit_crossed_amount = fields.Char(string="Limit Crossed Amount")


    def action_no(self):
        return {'type': 'ir.actions.act_window_close'}
