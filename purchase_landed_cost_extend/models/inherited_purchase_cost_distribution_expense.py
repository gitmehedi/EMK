from odoo import fields, models, api


class InheritedPurchaseCostDistributionExpense(models.Model):
    _inherit = 'purchase.cost.distribution.expense'

    account_id = fields.Many2one('account.account', string="Account")

    ref = fields.Char(string="Reference", required=True)
