from odoo import models, fields, api,_


class BudgetAccountWizard(models.TransientModel):
    _name = 'budget.account.wizard'

    account_ids = fields.Many2many('account.account', 'account_budget_wiz_rel', 'budget_wiz_id', 'account_id', 'Accounts',
                                   domain=[('internal_type', '!=', 'view'),('deprecated', '=', False)])

    def action_proceed_accounts(self):
        if self.account_ids:
            bottom_line_obj = self.env['bottom.line.budget'].search([('id','=',self.env.context.get('active_id'))])
            vals = []
            for obj in self.account_ids:
                vals.append((0, 0, {'bottom_line_account_id': obj.id,
                                    'planned_amount': 0,
                                    }))
            bottom_line_obj.bottom_line_budgets = vals