from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning


class InheritedPurchaseCostDistributionExpense(models.Model):
    _inherit = 'purchase.cost.distribution.expense'

    account_id = fields.Many2one('account.account', string="Account")
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", store=False)

    @api.one
    @api.constrains('expense_amount')
    def _check_expense_amount(self):
        if self.expense_amount < 0.0:
            raise UserError('Expense Amount should be negative!')

    ref = fields.Char(string="Reference", required=True)
