from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning


class InheritedPurchaseCostDistributionExpense(models.Model):
    _inherit = 'purchase.cost.distribution.expense'

    account_id = fields.Many2one('account.account', string="Account")

    @api.depends('distribution')
    def compute_anl_acc(self):
        for rec in self:
            if rec.distribution:
                if rec.distribution.lc_id:
                    rec.analytic_account_id = rec.distribution.lc_id.analytic_account_id.id
                else:
                    rec.analytic_account_id = False

    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account",
                                          compute='compute_anl_acc')

    @api.one
    @api.constrains('expense_amount')
    def _check_expense_amount(self):
        if self.expense_amount < 0.0:
            raise ValidationError('Expense Amount should not be negative!')

    ref = fields.Char(string="Reference", required=True)

    @api.model
    def create(self, vals):
        res = super(InheritedPurchaseCostDistributionExpense, self).create(vals)
        res.distribution.write({'analytic_account': res.distribution.lc_id.analytic_account_id.id})
