from datetime import timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError,Warning, ValidationError

# ---------------------------------------------------------
# Budgets Distribution
# ---------------------------------------------------------
class BranchDistribution(models.Model):
    _name = "budget.distribution"
    _inherit = ['mail.thread','ir.needaction_mixin']
    _description = "Budget Distribution"

    name = fields.Char('Budget Name',readonly=True, track_visibility='onchange')
    creating_user_id = fields.Many2one('res.users', 'Responsible', readonly=True, track_visibility='onchange',
                                       default=lambda self: self.env.user)
    approved_user_id = fields.Many2one('res.users', 'Approved By', readonly=True, track_visibility='onchange',
                                       default=lambda self: self.env.user)
    account_id = fields.Many2one('account.account', string='Account', required=True,readonly=True,
                                 default=lambda self: self.env.context.get('default_account_id'),
                                 track_visibility='onchange')
    planned_amount = fields.Float('Planned Amount',default=lambda self: self.env.context.get('default_planned_amount'),
                                  readonly=True,track_visibility='onchange')
    remaining_amount = fields.Float('Remaining Planned Amount',readonly=True,
                                    compute='_compute_remaining_amount',store=True)
    total_practical_amount = fields.Float('Total Practical Amount',readonly=True,
                                          compute='_compute_total_practical_amount',
                                          help='Sum of Practical Amount')
    rem_exceed_amount = fields.Float('Remaining/Exceed Amount', readonly=True,
                                     compute='_compute_rem_exceed_amount',
                                     help='Subtractions of Practical Amount and Planned Amount')
    fiscal_year = fields.Many2one('date.range', string='Date range', track_visibility='onchange',
                                  default=lambda self: self.env.context.get('default_fiscal_year'),
                                  readonly=True, required=True)
    date_from = fields.Date(related='fiscal_year.date_start', string='Start Date', readonly=True)
    date_to = fields.Date(related='fiscal_year.date_end', string='End Date', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('approve', 'Approved'),
    ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')
    approve_date = fields.Datetime(string='Approve Date', readonly=True, track_visibility='onchange')
    branch_budget_lines = fields.One2many('branch.budget.line', 'branch_budget_id',readonly=True,
                                          states={'draft': [('readonly', False)]},
                                          string='Lines')
    cost_centre_budget_lines = fields.One2many('cost.centre.budget.line', 'cost_centre_budget_id', readonly=True,
                                               states={'draft': [('readonly', False)]},
                                               string='Lines')
    budget_distribution_history_ids = fields.One2many('budget.distribution.history', 'budget_distribution_id', readonly=True,
                                                string='History Lines')
    bottom_line_budget_line = fields.Many2one('bottom.line.budget.line',
                                              string='Bottom line budget',
                                              default=lambda self: self.env.context.get('active_id'))
    active = fields.Boolean(default=True, track_visibility='onchange',compute='_compute_active')

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
        return super(BranchDistribution, self).unlink()

    @api.onchange('account_id')
    def onchange_account_id(self):
        if self.account_id:
            self.branch_budget_lines = []
            self.cost_centre_budget_lines = []
            branch_vals = []
            cost_vals =  []

            op_pool = self.env['operating.unit'].search([])
            for obj in op_pool:
                branch_vals.append((0, 0, {'operating_unit_id': obj.id,}))
            self.branch_budget_lines = branch_vals

            cost_pool = self.env['account.analytic.account'].search([])
            for obj in cost_pool:
                cost_vals.append((0, 0, {'analytic_account_id': obj.id,}))
            self.cost_centre_budget_lines = cost_vals


    @api.multi
    @api.depends('planned_amount','branch_budget_lines.planned_amount','cost_centre_budget_lines.planned_amount')
    def _compute_remaining_amount(self):
        for budget in self:
            if budget.planned_amount:
                branch_line_total_amount = sum(line.planned_amount for line in budget.branch_budget_lines)
                cost_line_total_amount = sum(line.planned_amount for line in budget.cost_centre_budget_lines)
                budget.remaining_amount = round(budget.planned_amount) - (round(branch_line_total_amount)+round(cost_line_total_amount))
            else:
                budget.remaining_amount = 0

    @api.constrains('remaining_amount')
    def _check_amount(self):
        self.ensure_one()
        if round(self.remaining_amount)>0:
            raise ValidationError(_('[ValidationError] Total amount not matched!\n'
                                    ' %s is still remaining.'% self.remaining_amount))
        elif round(self.remaining_amount)<0:
            raise ValidationError(_('[ValidationError] Total amount not matched!\n'
                                    ' %s is bigger then planned amount.'% -(self.remaining_amount)))
        return True

    def action_amendment(self):
        history_pools = self.env['budget.distribution.history']
        branch_history_line_pools = self.env['branch.budget.history.line']
        cost_history_line_pools = self.env['cost.centre.budget.history.line']
        res = {
            'name': self.name,
            'creating_user_id': self.creating_user_id.id,
            'approved_user_id': self.approved_user_id.id,
            'account_id': self.account_id.id,
            'planned_amount': self.planned_amount,
            'remaining_amount': self.remaining_amount,
            'fiscal_year': self.fiscal_year.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'approve_date': self.approve_date,
            'budget_distribution_id': self.id,
            'bottom_line_budget_line': self.bottom_line_budget_line.id,
            'active': self.active,
        }
        history = history_pools.create(res)
        if history:
            history_id = history.id

        for line in self.branch_budget_lines:
            lines = {
                'branch_budget_history_id': history_id,
                'operating_unit_id': line.operating_unit_id.id,
                'planned_amount': line.planned_amount,
                'practical_amount': line.practical_amount,
                'theoritical_amount': line.practical_amount,
                'active': self.active,
            }
            branch_history_line_pools.create(lines)

        for line in self.cost_centre_budget_lines:
            lines = {
                'cost_centre_budget_history_id': history_id,
                'analytic_account_id': line.analytic_account_id.id,
                'planned_amount': line.planned_amount,
                'practical_amount': line.practical_amount,
                'theoritical_amount': line.practical_amount,
                'active': self.active,
            }
            cost_history_line_pools.create(lines)

        self.write({'state': 'draft'})

    def _compute_active(self):
        if self.bottom_line_budget_line and self.bottom_line_budget_line.active ==False:
            self.active = False
        else:
            self.active = True

    @api.one
    @api.depends('branch_budget_lines.practical_amount','cost_centre_budget_lines.practical_amount')
    def _compute_total_practical_amount(self):
        for rec in self:
            rec.total_practical_amount = sum(line.practical_amount for line in rec.branch_budget_lines) + \
                                         sum(line.practical_amount for line in rec.cost_centre_budget_lines)

    @api.one
    @api.depends('total_practical_amount', 'planned_amount')
    def _compute_rem_exceed_amount(self):
        for rec in self:
            rec.rem_exceed_amount = rec.planned_amount - rec.total_practical_amount

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'draft')]

# ---------------------------------------------------------
# Branch wise Budgets Distribution
# ---------------------------------------------------------
class BudgetBranchDistributionLine(models.Model):
    _name = "branch.budget.line"
    _description = "Branch Budget Line"

    branch_budget_id = fields.Many2one('budget.distribution',string='Branch Budget')
    operating_unit_id = fields.Many2one('operating.unit',required=True, string='Branch')
    planned_amount = fields.Float('Planned Amount', required=True)
    practical_amount = fields.Float(string='Practical Amount',compute='_compute_practical_amount')
    remaining_amount = fields.Float(string='Remaining Amount',compute='_compute_remaining_amount')
    theoritical_amount = fields.Float(string='Theoretical Amount' ,compute='_compute_theoritical_amount')
    active = fields.Boolean(default=True,compute='_compute_active')

    def _compute_practical_amount(self):
        for line in self:
            result = 0.0
            acc_id = line.branch_budget_id.account_id.id
            date_to = line.branch_budget_id.date_to
            date_from = line.branch_budget_id.date_from
            acc_inv_ids = self.env['account.invoice'].search(
                [('date', '>=', date_from),
                 ('date', '<=', date_to),
                 ('state','!=','cancel')]).ids

            if line.operating_unit_id.id and acc_inv_ids:
                self.env.cr.execute("""
                    SELECT SUM(price_subtotal_without_vat)
                    FROM account_invoice_line
                    WHERE account_id=%s
                    AND invoice_id in %s
                    AND operating_unit_id=%s""",
                                    (acc_id,(tuple(acc_inv_ids)),line.operating_unit_id.id))
                result = self.env.cr.fetchone()[0] or 0.0
            line.practical_amount = result


    @api.multi
    @api.depends('planned_amount')
    def _compute_theoritical_amount(self):
        today = fields.Datetime.now()
        theo_amt = 0.00
        for line in self:
            line_date_to = line.branch_budget_id.date_to
            line_date_from = line.branch_budget_id.date_from
            end_today = fields.Datetime.from_string(today) + timedelta(days=1)
            end_date_to = fields.Datetime.from_string(line_date_to) + timedelta(days=1)

            line_timedelta = end_date_to - fields.Datetime.from_string(line_date_from)
            elapsed_timedelta = end_today - fields.Datetime.from_string(line_date_from)

            if elapsed_timedelta.days < 0:
                # If the budget line has not started yet, theoretical amount should be zero
                theo_amt = 0.00
            elif line_timedelta.days > 0 and fields.Datetime.from_string(today) < fields.Datetime.from_string(line_date_to):
                # If today is between the budget line date_from and date_to
                theo_amt = ((float(elapsed_timedelta.days) / float(line_timedelta.days))) * line.planned_amount
            else:
                theo_amt = line.planned_amount

            line.theoritical_amount = theo_amt

    def _compute_remaining_amount(self):
        for rec in self:
            rec.remaining_amount = rec.planned_amount - rec.practical_amount


    def _compute_active(self):
        if self.branch_budget_id and \
                        self.branch_budget_id.active ==False:
            self.active = False
        else:
            self.active = True

    @api.one
    @api.constrains('planned_amount')
    def _check_planned_amount(self):
        if self.planned_amount < 0:
            raise UserError('You can\'t give negative value!!!')

# ---------------------------------------------------------
# Cost Centre wise Budgets Distribution
# ---------------------------------------------------------
class CostCentreBudgetLine(models.Model):
    _name = "cost.centre.budget.line"
    _description = "Cost Centre Budget Line"

    cost_centre_budget_id = fields.Many2one('budget.distribution',string='Budget Distribution')
    analytic_account_id = fields.Many2one('account.analytic.account',required=True,string='Cost Centre')
    planned_amount = fields.Float('Planned Amount', required=True)
    practical_amount = fields.Float(string='Practical Amount',compute='_compute_practical_amount')
    remaining_amount = fields.Float(string='Remaining Amount', compute='_compute_remaining_amount')
    theoritical_amount = fields.Float(string='Theoretical Amount',compute='_compute_theoritical_amount')
    active = fields.Boolean(default=True, compute='_compute_active')

    def _compute_practical_amount(self):
        for line in self:
            result = 0.0
            acc_id = line.cost_centre_budget_id.account_id.id
            date_to = line.cost_centre_budget_id.date_to
            date_from = line.cost_centre_budget_id.date_from
            acc_inv_ids = self.env['account.invoice'].search(
                [('date', '>=', date_from),
                 ('date', '<=', date_to),
                 ('state','!=','cancel')]).ids

            if line.analytic_account_id.id and acc_inv_ids:
                self.env.cr.execute("""
                    SELECT SUM(price_subtotal_without_vat)
                    FROM account_invoice_line
                    WHERE account_id=%s
                    AND invoice_id in %s
                    AND account_analytic_id=%s""",
                (acc_id,(tuple(acc_inv_ids)),line.analytic_account_id.id))
                result = self.env.cr.fetchone()[0] or 0.0
            line.practical_amount = result


    @api.multi
    @api.depends('planned_amount')
    def _compute_theoritical_amount(self):
        today = fields.Datetime.now()
        theo_amt = 0.00
        for line in self:
            line_date_to = line.cost_centre_budget_id.date_to
            line_date_from = line.cost_centre_budget_id.date_from
            end_today = fields.Datetime.from_string(today) + timedelta(days=1)
            end_date_to = fields.Datetime.from_string(line_date_to) + timedelta(days=1)

            line_timedelta = end_date_to - fields.Datetime.from_string(line_date_from)
            elapsed_timedelta = end_today - fields.Datetime.from_string(line_date_from)

            if elapsed_timedelta.days < 0:
                # If the budget line has not started yet, theoretical amount should be zero
                theo_amt = 0.00
            elif line_timedelta.days > 0 and fields.Datetime.from_string(today) < fields.Datetime.from_string(line_date_to):
                # If today is between the budget line date_from and date_to
                theo_amt = ((float(elapsed_timedelta.days) / float(line_timedelta.days))) * line.planned_amount
            else:
                theo_amt = line.planned_amount

            line.theoritical_amount = theo_amt

    def _compute_remaining_amount(self):
        for rec in self:
            rec.remaining_amount = rec.planned_amount - rec.practical_amount

    def _compute_active(self):
        if self.cost_centre_budget_id and \
                        self.cost_centre_budget_id.active == False:
            self.active = False
        else:
            self.active = True

    @api.one
    @api.constrains('planned_amount')
    def _check_planned_amount(self):
        if self.planned_amount < 0:
            raise UserError('You can\'t give negative value!!!')