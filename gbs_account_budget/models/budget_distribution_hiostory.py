from odoo import api, fields, models, _

# ---------------------------------------------------------
# Branch wise Budgets Distribution History
# ---------------------------------------------------------
class BranchBudgetHistory(models.Model):
    _name = "branch.budget.history"
    _inherit = ['mail.thread']
    _description = "Branch Budget History"

    name = fields.Char('Budget Name',readonly=True, track_visibility='onchange')
    creating_user_id = fields.Many2one('res.users', 'Responsible', readonly=True, track_visibility='onchange')
    approved_user_id = fields.Many2one('res.users', 'Approved By', readonly=True, track_visibility='onchange')
    account_id = fields.Many2one('account.account', string='Account',readonly=True,track_visibility='onchange')
    planned_amount = fields.Float('Planned Amount',readonly=True,track_visibility='onchange')
    remaining_amount = fields.Float('Remaining Amount',readonly=True)
    fiscal_year = fields.Many2one('date.range', string='Date range', track_visibility='onchange',readonly=True)
    date_from = fields.Date(string='Start Date', readonly=True)
    date_to = fields.Date(string='End Date', readonly=True)
    approve_date = fields.Datetime(string='Approve Date', readonly=True, track_visibility='onchange')
    branch_budget_lines = fields.One2many('branch.budget.history.line', 'branch_budget_history_id',readonly=True,
                                          string='Lines')
    bottom_line_budget_line = fields.Many2one('bottom.line.budget.line',string='Bottom line budget')
    branch_budget_id = fields.Many2one('branch.budget',string='Branch budget distribution')


class BudgetBranchHistoryLine(models.Model):
    _name = "branch.budget.history.line"
    _description = "Branch Budget History Line"

    branch_budget_history_id = fields.Many2one('branch.budget.history',string='Branch Budget')
    operating_unit_id = fields.Many2one('operating.unit',required=True, string='Branch')
    planned_amount = fields.Float('Planned Amount', required=True)
    practical_amount = fields.Float(string='Practical Amount')
    theoritical_amount = fields.Float(string='Theoretical Amount')



# ---------------------------------------------------------
# Cost Centre wise Budgets Distribution History
# ---------------------------------------------------------
class CostCentreBudgetHistory(models.Model):
    _name = "cost.centre.budget.history"
    _inherit = ['mail.thread']
    _description = "Branch Budget History"

    name = fields.Char('Budget Name',readonly=True, track_visibility='onchange')
    creating_user_id = fields.Many2one('res.users', 'Responsible', readonly=True, track_visibility='onchange')
    approved_user_id = fields.Many2one('res.users', 'Approved By', readonly=True, track_visibility='onchange')
    account_id = fields.Many2one('account.account', string='Account',readonly=True,track_visibility='onchange')
    planned_amount = fields.Float('Planned Amount',readonly=True,track_visibility='onchange')
    remaining_amount = fields.Float('Remaining Amount',readonly=True)
    fiscal_year = fields.Many2one('date.range', string='Date range', track_visibility='onchange',readonly=True)
    date_from = fields.Date(string='Start Date', readonly=True)
    date_to = fields.Date(string='End Date', readonly=True)
    approve_date = fields.Datetime(string='Approve Date', readonly=True, track_visibility='onchange')
    cost_centre_budget_lines = fields.One2many('cost.centre.budget.history.line', 'cost_centre_budget_history_id',readonly=True,
                                          string='Lines')
    bottom_line_budget_line = fields.Many2one('bottom.line.budget.line',string='Bottom line budget')
    costcentre_budget_id = fields.Many2one('cost.centre.budget',string='Branch budget distribution')


class CostCentreBudgetHistoryLine(models.Model):
    _name = "cost.centre.budget.history.line"
    _description = "Cost Centre Budget History Line"

    cost_centre_budget_history_id = fields.Many2one('cost.centre.budget.history',string='Cost Centre Budget')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Cost Centre')
    planned_amount = fields.Float('Planned Amount', required=True)
    practical_amount = fields.Float(string='Practical Amount')
    theoritical_amount = fields.Float(string='Theoretical Amount')
