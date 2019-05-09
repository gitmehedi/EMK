from odoo import api, fields, models, _
from odoo.exceptions import UserError

# ---------------------------------------------------------
# Branch wise Budgets Distribution
# ---------------------------------------------------------
class BranchBudget(models.Model):
    _name = "branch.budget"
    _inherit = ['mail.thread']
    _description = "Branch Budget"

    name = fields.Char('Budget Name', required=True, readonly=True,
                       states={'draft': [('readonly', False)]}, track_visibility='onchange')
    creating_user_id = fields.Many2one('res.users', 'Responsible', readonly=True, track_visibility='onchange',
                                       default=lambda self: self.env.user)
    approved_user_id = fields.Many2one('res.users', 'Approved By', readonly=True, track_visibility='onchange',
                                       default=lambda self: self.env.user)
    account_id = fields.Many2one('account.account', string='Account', required=True,readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 track_visibility='onchange')
    planned_amount = fields.Float('Planned Amount', required=True,readonly=True,
                                  states={'draft': [('readonly', False)]})
    fiscal_year = fields.Many2one('date.range', string='Date range', track_visibility='onchange',
                                  readonly=True, required=True, states={'draft': [('readonly', False)]})
    date_from = fields.Date(related='fiscal_year.date_start', string='Start Date', readonly=True)
    date_to = fields.Date(related='fiscal_year.date_end', string='End Date', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('approve', 'Approved'),
    ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')
    prepare_date = fields.Datetime(string='Prepare Date', readonly=True, track_visibility='onchange')
    confirm_date = fields.Datetime(string='Confirm Date', readonly=True, track_visibility='onchange')
    approve_date = fields.Datetime(string='Approve Date', readonly=True, track_visibility='onchange')
    branch_budget_lines = fields.One2many('branch.budget.line', 'branch_budget_id',
                                                string='Lines')

    @api.multi
    def action_budget_confirm(self):
        vals = {'state': 'confirm',
                'confirm_date': fields.Datetime.now(),
                }
        self.write(vals)

    @api.multi
    def action_budget_approve(self):
        vals = {'state': 'approve',
                'approve_date': fields.Datetime.now(),
                'approved_user_id': self.env.user.id
                }
        self.write(vals)

    @api.multi
    def action_budget_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_budget_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You cannot delete a record which is not in draft state!'))
        return super(BranchBudget, self).unlink()

    @api.onchange('account_id')
    def onchange_account_id(self):
        if self.account_id:
            self.branch_budget_lines = []
            vals = []
            op_pool = self.env['operating.unit'].search([])
            line_planned_amount = self.planned_amount / len(op_pool)
            for obj in op_pool:
                vals.append((0, 0, {'account_id': self.account_id.id,
                                    'operating_unit_id': obj.id,
                                    'planned_amount': line_planned_amount,
                                    }))
            self.branch_budget_lines = vals

    @api.onchange('planned_amount')
    def onchange_planned_amount(self):
        if self.planned_amount and self.branch_budget_lines:
            for line in self.branch_budget_lines:
                line.planned_amount = self.planned_amount/len(self.branch_budget_lines)


class BudgetBranchDistributionLine(models.Model):
    _name = "branch.budget.line"
    _description = "Branch Budget Line"

    branch_budget_id = fields.Many2one('branch.budget',string='Branch Budget')
    account_id = fields.Many2one('account.account',string='Accounts')
    operating_unit_id = fields.Many2one('operating.unit', string='Branch')
    planned_amount = fields.Float('Planned Amount', required=True)
    practical_amount = fields.Float(string='Practical Amount', store=True)
    theoritical_amount = fields.Float(string='Theoretical Amount', store=True)


# ---------------------------------------------------------
# Cost Center wise Budgets Distribution
# ---------------------------------------------------------
class CostCenterBudget(models.Model):
    _name = "cost.center.budget"
    _inherit = ['mail.thread']
    _description = "Cost Center Budget"

    name = fields.Char('Budget Name', required=True, readonly=True,
                       states={'draft': [('readonly', False)]}, track_visibility='onchange')
    creating_user_id = fields.Many2one('res.users', 'Responsible', readonly=True, track_visibility='onchange',
                                       default=lambda self: self.env.user)
    approved_user_id = fields.Many2one('res.users', 'Approved By', readonly=True, track_visibility='onchange',
                                       default=lambda self: self.env.user)
    account_id = fields.Many2one('account.account', string='Account', required=True,readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 track_visibility='onchange')
    planned_amount = fields.Float('Planned Amount', required=True,readonly=True,
                                  states={'draft': [('readonly', False)]})
    fiscal_year = fields.Many2one('date.range', string='Date range', track_visibility='onchange',
                                  readonly=True, required=True, states={'draft': [('readonly', False)]})
    date_from = fields.Date(related='fiscal_year.date_start', string='Start Date', readonly=True)
    date_to = fields.Date(related='fiscal_year.date_end', string='End Date', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('approve', 'Approved'),
    ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')
    prepare_date = fields.Datetime(string='Prepare Date', readonly=True, track_visibility='onchange')
    confirm_date = fields.Datetime(string='Confirm Date', readonly=True, track_visibility='onchange')
    approve_date = fields.Datetime(string='Approve Date', readonly=True, track_visibility='onchange')
    cost_center_budget_lines = fields.One2many('cost.center.budget.line', 'cost_center_budget_id',
                                                string='Lines')

    @api.multi
    def action_budget_confirm(self):
        vals = {'state': 'confirm',
                'confirm_date': fields.Datetime.now(),
                }
        self.write(vals)

    @api.multi
    def action_budget_approve(self):
        vals = {'state': 'approve',
                'approve_date': fields.Datetime.now(),
                'approved_user_id': self.env.user.id
                }
        self.write(vals)

    @api.multi
    def action_budget_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_budget_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You cannot delete a record which is not in draft state!'))
        return super(CostCenterBudget, self).unlink()

    @api.onchange('account_id')
    def onchange_account_id(self):
        if self.account_id:
            self.cost_center_budget_lines = []
            vals = []
            op_pool = self.env['account.analytic.account'].search([])
            line_planned_amount = self.planned_amount / len(op_pool)
            for obj in op_pool:
                vals.append((0, 0, {'account_id': self.account_id.id,
                                    'analytic_account_id': obj.id,
                                    'planned_amount': line_planned_amount,
                                    }))
            self.cost_center_budget_lines = vals

    @api.onchange('planned_amount')
    def onchange_planned_amount(self):
        if self.planned_amount and self.cost_center_budget_lines:
            for line in self.cost_center_budget_lines:
                line.planned_amount = self.planned_amount / len(self.cost_center_budget_lines)

class CostCenterBudgetDistributionLine(models.Model):
    _name = "cost.center.budget.line"
    _description = "Cost Center Budget Line"

    cost_center_budget_id = fields.Many2one('budget.distribution',string='Budget Distribution')
    account_id = fields.Many2one('account.account',string='Accounts')
    analytic_account_id = fields.Many2one('account.analytic.account',string='Cost Center')
    planned_amount = fields.Float('Planned Amount', required=True)
    practical_amount = fields.Float(string='Practical Amount', store=True)
    theoritical_amount = fields.Float(string='Theoretical Amount', store=True)