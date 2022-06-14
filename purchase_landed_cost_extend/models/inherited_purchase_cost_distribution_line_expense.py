from odoo import fields, models, api


class InheritedPurchaseCostDistributionLineExpense(models.Model):
    _inherit = "purchase.cost.distribution.line.expense"

    account_id = fields.Many2one('account.account', string="Account")
