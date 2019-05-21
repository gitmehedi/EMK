from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError,Warning, ValidationError
# ---------------------------------------------------------
# Cost Centre wise Budgets Distribution
# ---------------------------------------------------------
class CostCentreBudget(models.Model):
    _name = "cost.centre.budget"
    _inherit = ['mail.thread','ir.needaction_mixin']
    _description = "Cost Centre Budget"

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
    remaining_amount = fields.Float('Remaining Amount', readonly=True,
                                    compute='_compute_remaining_amount', store=True)
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
    cost_centre_budget_lines = fields.One2many('cost.centre.budget.line', 'cost_centre_budget_id',readonly=True,
                                               states={'draft': [('readonly', False)]},
                                               string='Lines')
    bottom_line_budget_line = fields.Many2one('bottom.line.budget.line',
                                              string='Bottom line budget',
                                              default=lambda self: self.env.context.get('active_id'))
    costcentre_budget_history_ids = fields.One2many('cost.centre.budget.history', 'costcentre_budget_id', readonly=True,
                                                string='History Lines')
    active = fields.Boolean(default=True, track_visibility='onchange', compute='_compute_active')

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
        return super(CostCentreBudget, self).unlink()


    @api.onchange('account_id')
    def onchange_account_id(self):
        if self.account_id:
            self.cost_centre_budget_lines = []
            vals = []
            op_pool = self.env['account.analytic.account'].search([])
            line_planned_amount = self.planned_amount / len(op_pool)
            for obj in op_pool:
                vals.append((0, 0, {'analytic_account_id': obj.id,
                                    # 'planned_amount': line_planned_amount,
                                    }))
            self.cost_centre_budget_lines = vals

    @api.multi
    @api.depends('planned_amount', 'cost_centre_budget_lines.planned_amount')
    def _compute_remaining_amount(self):
        for budget in self:
            if budget.planned_amount:
                line_total_amount = sum(line.planned_amount for line in budget.cost_centre_budget_lines)
                budget.remaining_amount = round(budget.planned_amount) - round(line_total_amount)
            else:
                budget.remaining_amount = 0

    @api.constrains('remaining_amount')
    def _check_amount(self):
        self.ensure_one()
        if round(self.remaining_amount) > 0:
            raise ValidationError(_('[ValidationError] Total amount not matched!\n'
                                    ' %s is still remaining.' % self.remaining_amount))
        elif round(self.remaining_amount) < 0:
            raise ValidationError(_('[ValidationError] Total amount not matched!\n'
                                    ' %s is bigger then planned amount.' % -(self.remaining_amount)))
        return True

    def action_amendment(self):
        history_pools = self.env['cost.centre.budget.history']
        history_line_pools = self.env['cost.centre.budget.history.line']
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
            'costcentre_budget_id': self.id,
            'bottom_line_budget_line': self.bottom_line_budget_line.id,
            'active': self.active,
        }
        history = history_pools.create(res)
        if history:
            history_id = history.id

        for line in self.cost_centre_budget_lines:
            lines = {
                'cost_centre_budget_history_id': history_id,
                'analytic_account_id': line.analytic_account_id.id,
                'planned_amount': line.planned_amount,
                'practical_amount': line.practical_amount,
                'theoritical_amount': line.practical_amount,
                'active': self.active,
            }
            history_line_pools.create(lines)

        self.write({'state': 'draft'})

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'draft')]

    def _compute_active(self):
        if self.bottom_line_budget_line and self.bottom_line_budget_line.active == False:
            self.active = False
        else:
            self.active = True


class CostCentreBudgetLine(models.Model):
    _name = "cost.centre.budget.line"
    _description = "Cost Centre Budget Line"

    cost_centre_budget_id = fields.Many2one('cost.centre.budget',string='Budget Distribution')
    analytic_account_id = fields.Many2one('account.analytic.account',required=True,string='Cost Centre')
    planned_amount = fields.Float('Planned Amount', required=True)
    practical_amount = fields.Float(string='Practical Amount',compute='_compute_practical_amount')
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

    def _compute_active(self):
        if self.cost_centre_budget_id.bottom_line_budget_line and \
                        self.cost_centre_budget_id.bottom_line_budget_line.active == False:
            self.active = False
        else:
            self.active = True