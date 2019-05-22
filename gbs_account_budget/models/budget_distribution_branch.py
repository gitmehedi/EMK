from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError,Warning, ValidationError

# ---------------------------------------------------------
# Branch wise Budgets Distribution
# ---------------------------------------------------------
class BranchBudget(models.Model):
    _name = "branch.budget"
    _inherit = ['mail.thread','ir.needaction_mixin']
    _description = "Branch Budget"

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
    remaining_amount = fields.Float('Remaining Amount',readonly=True,
                                    compute='_compute_remaining_amount',store=True)
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
    bottom_line_budget_line = fields.Many2one('bottom.line.budget.line',
                                              string='Bottom line budget',
                                              default=lambda self: self.env.context.get('active_id'))
    branch_budget_history_ids = fields.One2many('branch.budget.history', 'branch_budget_id', readonly=True,
                                                string='History Lines')
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
        return super(BranchBudget, self).unlink()

    # @api.onchange('fiscal_year')
    # def _onchange_fiscal_year(self):
    #     if self.fiscal_year:
    #         res = {}
    #         self.account_id = []
    #         self.branch_budget_lines = []
    #         self.planned_amount = 0.0
    #         budget_objs = self.search([('fiscal_year', '=', self.fiscal_year.id)])
    #         pre_account_ids = [i.account_id.id for i in budget_objs]
    #         res['domain'] = {
    #             'account_id': [('id', 'not in', pre_account_ids)],
    #         }
    #         return res


    @api.onchange('account_id')
    def onchange_account_id(self):
        if self.account_id:
            self.branch_budget_lines = []
            vals = []
            op_pool = self.env['operating.unit'].search([])
            line_planned_amount = self.planned_amount / len(op_pool)
            for obj in op_pool:
                vals.append((0, 0, {'operating_unit_id': obj.id,
                                    # 'planned_amount': line_planned_amount,
                                    }))
            self.branch_budget_lines = vals


    # @api.onchange('planned_amount')
    # def onchange_planned_amount(self):
    #     if self.planned_amount and self.branch_budget_lines:
    #         for line in self.branch_budget_lines:
    #             line.planned_amount = self.planned_amount/len(self.branch_budget_lines)
    #     elif not self.planned_amount and self.branch_budget_lines:
    #         for line in self.branch_budget_lines:
    #             line.planned_amount = 0.0

    @api.multi
    @api.depends('planned_amount','branch_budget_lines.planned_amount')
    def _compute_remaining_amount(self):
        for budget in self:
            if budget.planned_amount:
                line_total_amount = sum(line.planned_amount for line in budget.branch_budget_lines)
                budget.remaining_amount = round(budget.planned_amount) - round(line_total_amount)
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
        history_pools = self.env['branch.budget.history']
        history_line_pools = self.env['branch.budget.history.line']
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
            'branch_budget_id': self.id,
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
            history_line_pools.create(lines)

        self.write({'state': 'draft'})

    def _compute_active(self):
        if self.bottom_line_budget_line and self.bottom_line_budget_line.active ==False:
            self.active = False
        else:
            self.active = True

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'draft')]


class BudgetBranchDistributionLine(models.Model):
    _name = "branch.budget.line"
    _description = "Branch Budget Line"

    branch_budget_id = fields.Many2one('branch.budget',string='Branch Budget')
    operating_unit_id = fields.Many2one('operating.unit',required=True, string='Branch')
    planned_amount = fields.Float('Planned Amount', required=True)
    practical_amount = fields.Float(string='Practical Amount',compute='_compute_practical_amount')
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
