from odoo import api, fields, models, _

# ---------------------------------------------------------
# Budgets Distribution History
# ---------------------------------------------------------
class BudgetDistributionHistory(models.Model):
    _name = "budget.distribution.history"
    _inherit = ['mail.thread']
    _description = "Budget Distribution History"

    name = fields.Char('Budget Name',readonly=True, track_visibility='onchange')
    creating_user_id = fields.Many2one('res.users', 'Responsible', readonly=True, track_visibility='onchange')
    approved_user_id = fields.Many2one('res.users', 'Approved By', readonly=True, track_visibility='onchange')
    account_id = fields.Many2one('account.account', string='Account',readonly=True,track_visibility='onchange')
    planned_amount = fields.Float('Planned Amount',readonly=True,track_visibility='onchange')
    remaining_amount = fields.Float('Remaining Amount',readonly=True)
    fiscal_year = fields.Many2one('date.range', string='Period', track_visibility='onchange',readonly=True)
    date_from = fields.Date(string='Start Date', readonly=True)
    date_to = fields.Date(string='End Date', readonly=True)
    approve_date = fields.Datetime(string='Approve Date', readonly=True, track_visibility='onchange')
    budget_distribution_history_lines = fields.One2many('budget.distribution.history.line', 'budget_distribution_history_id',
                                          readonly=True,string='Lines')
    bottom_line_budget_id = fields.Many2one('bottom.line.budget.line',string='Bottom line budget')
    budget_distribution_id = fields.Many2one('budget.distribution',string='budget distribution')
    active = fields.Boolean(string='Active')

# ---------------------------------------------------------
# Branch wise Budgets Distribution History
# ---------------------------------------------------------
class BranchDistributionHistoryLine(models.Model):
    _name = "budget.distribution.history.line"
    _description = "Budget Distribution History Line"

    budget_distribution_history_id = fields.Many2one('budget.distribution.history',string='Budget Distribution History')
    operating_unit_id = fields.Many2one('operating.unit',string='Branch')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Cost Centre', required=True)
    planned_amount = fields.Float('Planned Amount', required=True)
    practical_amount = fields.Float(string='Practical Amount')
    theoritical_amount = fields.Float(string='Theoretical Amount')
    active = fields.Boolean(string='Active')