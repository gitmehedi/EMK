from odoo import api, fields, models, _
from odoo.exceptions import UserError,Warning, ValidationError

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
    remaining_amount = fields.Float('Remaining Amount',readonly=True,
                                    compute='_compute_remaining_amount',store=True)
    fiscal_year = fields.Many2one('date.range', string='Date range', track_visibility='onchange',
                                  domain="[('type_id.fiscal_year', '=', True)]",
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
    branch_budget_lines = fields.One2many('branch.budget.line', 'branch_budget_id',readonly=True,
                                          states={'draft': [('readonly', False)]},
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

    @api.onchange('fiscal_year')
    def _onchange_fiscal_year(self):
        if self.fiscal_year:
            res = {}
            self.account_id = []
            self.branch_budget_lines = []
            self.planned_amount = 0.0
            budget_objs = self.search([('fiscal_year', '=', self.fiscal_year.id)])
            pre_account_ids = [i.account_id.id for i in budget_objs]
            res['domain'] = {
                'account_id': [('id', 'not in', pre_account_ids)],
            }
            return res


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
        elif not self.planned_amount and self.branch_budget_lines:
            for line in self.branch_budget_lines:
                line.planned_amount = 0.0

    @api.multi
    @api.depends('planned_amount','branch_budget_lines.planned_amount')
    def _compute_remaining_amount(self):
        for budget in self:
            if budget.planned_amount:
                line_total_amount = sum(line.planned_amount for line in budget.branch_budget_lines)
                budget.remaining_amount = budget.planned_amount - line_total_amount
                # if line_total_amount <= budget.planned_amount:
                #     budget.remaining_amount = budget.planned_amount - line_total_amount
                # else:
                #     raise ValidationError(_(
                #         '[ValidationError] Total amount in branches can not '
                #         'be bigger then Account planned amount!'))
            else:
                budget.remaining_amount = 0

    @api.constrains('remaining_amount')
    def _check_amount(self):
        self.ensure_one()
        if self.remaining_amount>0:
            raise ValidationError(_('[ValidationError] Total amount not matched!\n'
                                    ' %s is still remaining.'% self.remaining_amount))
        elif self.remaining_amount<0:
            raise ValidationError(_('[ValidationError] Total amount not matched!\n'
                                    ' %s is bigger then planned amount.'% -(self.remaining_amount)))
        return True


class BudgetBranchDistributionLine(models.Model):
    _name = "branch.budget.line"
    _description = "Branch Budget Line"

    branch_budget_id = fields.Many2one('branch.budget',string='Branch Budget')
    account_id = fields.Many2one('account.account',string='Accounts')
    operating_unit_id = fields.Many2one('operating.unit',required=True, string='Branch')
    planned_amount = fields.Float('Planned Amount', required=True)
    practical_amount = fields.Float(string='Practical Amount', store=True)
    theoritical_amount = fields.Float(string='Theoretical Amount', store=True)

    def _compute_practical_amount(self):
        for line in self:
            result = 0.0
            acc_ids = line.general_budget_id.account_ids.ids
            if not acc_ids:
                raise UserError(_("The Budget '%s' has no accounts!") % ustr(line.general_budget_id.name))
            date_to = self.env.context.get('wizard_date_to') or line.date_to
            date_from = self.env.context.get('wizard_date_from') or line.date_from
            if line.analytic_account_id.id:
                self.env.cr.execute("""
                    SELECT SUM(amount)
                    FROM account_analytic_line
                    WHERE account_id=%s
                        AND (date between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))
                        AND general_account_id=ANY(%s)""",
                                    (line.analytic_account_id.id, date_from, date_to, acc_ids,))
                result = self.env.cr.fetchone()[0] or 0.0
            line.practical_amount = result




# ---------------------------------------------------------
# Cost Centre wise Budgets Distribution
# ---------------------------------------------------------
class CostCenterBudget(models.Model):
    _name = "cost.center.budget"
    _inherit = ['mail.thread']
    _description = "Cost Centre Budget"

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
    remaining_amount = fields.Float('Remaining Amount', readonly=True,
                                    compute='_compute_remaining_amount', store=True)
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
    cost_center_budget_lines = fields.One2many('cost.center.budget.line', 'cost_center_budget_id',readonly=True,
                                               states={'draft': [('readonly', False)]},
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

    @api.onchange('fiscal_year')
    def _onchange_fiscal_year(self):
        if self.fiscal_year:
            res = {}
            self.account_id = []
            self.cost_center_budget_lines = []
            self.planned_amount = 0.0
            budget_objs = self.search([('fiscal_year', '=', self.fiscal_year.id)])
            pre_account_ids = [i.account_id.id for i in budget_objs]
            res['domain'] = {
                'account_id': [('id', 'not in', pre_account_ids)],
            }
            return res

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
        elif not self.planned_amount and self.cost_center_budget_lines:
            for line in self.cost_center_budget_lines:
                line.planned_amount = 0.0

    @api.multi
    @api.depends('planned_amount', 'cost_center_budget_lines.planned_amount')
    def _compute_remaining_amount(self):
        for budget in self:
            if budget.planned_amount:
                line_total_amount = sum(line.planned_amount for line in budget.cost_center_budget_lines)
                budget.remaining_amount = budget.planned_amount - line_total_amount
            else:
                budget.remaining_amount = 0

    @api.constrains('remaining_amount')
    def _check_amount(self):
        self.ensure_one()
        if self.remaining_amount > 0:
            raise ValidationError(_('[ValidationError] Total amount not matched!\n'
                                    ' %s is still remaining.' % self.remaining_amount))
        elif self.remaining_amount < 0:
            raise ValidationError(_('[ValidationError] Total amount not matched!\n'
                                    ' %s is bigger then planned amount.' % -(self.remaining_amount)))
        return True



class CostCenterBudgetDistributionLine(models.Model):
    _name = "cost.center.budget.line"
    _description = "Cost Centre Budget Line"

    cost_center_budget_id = fields.Many2one('budget.distribution',string='Budget Distribution')
    account_id = fields.Many2one('account.account',string='Accounts')
    analytic_account_id = fields.Many2one('account.analytic.account',required=True,string='Cost Centre')
    planned_amount = fields.Float('Planned Amount', required=True)
    practical_amount = fields.Float(string='Practical Amount', store=True)
    theoritical_amount = fields.Float(string='Theoretical Amount', store=True)