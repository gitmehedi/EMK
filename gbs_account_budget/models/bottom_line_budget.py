from odoo import api, fields, models, _
from odoo.exceptions import UserError

# ---------------------------------------------------------
# Bottom Line Budgets
# ---------------------------------------------------------
# class BottomLineBudgetTemp(models.Model):
#     _name = "bottom.line.budget.temp"
#     _inherit = ['mail.thread']
#     _order = "name"
#     _description = "Bottom Line Budgetary Template"
#
#     name = fields.Char('Name',required=True, size=50, track_visibility='onchange')
#     date_create = fields.Datetime('Date', readonly=True, default=lambda self: fields.Datetime.now())
#     bottom_line_budgets = fields.One2many('bottom.line.budget.temp.line', 'bottom_line_budget',
#                                            string='Bottom Lines')
#
#     @api.multi
#     def action_select_accounts(self):
#         res = self.env.ref('gbs_account_budget.view_bottom_line_wizard_form')
#
#         result = {'name': _('Bottom Line'),
#                   'view_type': 'form',
#                   'view_mode': 'form',
#                   'view_id': res and res.id or False,
#                   'res_model': 'bottom.line.wizard',
#                   'type': 'ir.actions.act_window',
#                   'target': 'new',
#                   'nodestroy': True,
#                   }
#
#         return result

class BottomLineBudget(models.Model):
    _name = "bottom.line.budget"
    _inherit = ['mail.thread']
    _order = "name"
    _description = "Bottom Line Budget"

    name = fields.Char('Name',required=True, size=50, track_visibility='onchange')
    date_create = fields.Datetime('Date', readonly=True, default=lambda self: fields.Datetime.now())
    bottom_line_budgets = fields.One2many('bottom.line.budget.line', 'bottom_line_budget',
                                          string='Bottom Lines')
    planned_amount = fields.Float('Planned Amount', required=True)
    level_id = fields.Many2one('account.account.level', string='Level', required=True,
                               track_visibility='onchange')
    account_id = fields.Many2one('account.account', string='Account',required=True,
                                 track_visibility='onchange')

    @api.onchange('level_id')
    def onchange_level_id(self):
        if self.level_id:
            res = {}
            self.account_id = []
            res['domain'] = {
                'account_id': [('level_id','=',self.level_id.id)],
            }
            return res

    @api.onchange('account_id')
    def onchange_account_id(self):
        if self.account_id:
            self.bottom_line_budgets = []
            vals = []
            accounts_pool = self.env['account.account'].search([('parent_id', '=', self.account_id.id)])
            self.planned_amount = self.env['top.line.budget.lines'].search([('account_id', '=', self.account_id.id)]).planned_amount
            line_planned_amount = self.planned_amount/len(accounts_pool)
            for obj in accounts_pool:
                vals.append((0, 0, {'top_line_account_id': self.account_id.id,
                                    'bottom_line_account_id': obj.id,
                                    'planned_amount': line_planned_amount,
                                    }))
            self.bottom_line_budgets = vals

class BottomLineBudgetLine(models.Model):
    _name = "bottom.line.budget.line"
    _description = "Bottom Line Budget Line"

    bottom_line_budget = fields.Many2one('bottom.line.budget',string='Bottom line budget')
    top_line_account_id = fields.Many2one('account.account',string='Top Line Accounts')
    bottom_line_account_id = fields.Many2one('account.account',string='Bottom Line Accounts')
    planned_amount = fields.Float('Planned Amount', required=True)



class BudgetBranchDistribution(models.Model):
    _name = "budget.branch.distribution"
    _inherit = ['mail.thread']
    _description = "Budget Branch Distribution"

    account_id = fields.Many2one('account.account', string='Account', required=True,
                                 track_visibility='onchange')
    planned_amount = fields.Float('Planned Amount', required=True)
    branch_budget_lines = fields.One2many('budget.branch.distribution.line', 'branch_budget_id',
                                          string='Lines')

    @api.onchange('account_id')
    def onchange_account_id(self):
        if self.account_id:
            self.branch_budget_lines = []
            vals = []
            # ampount_pool = self.env['account.account'].search([('parent_id', '=', self.account_id.id)])
            op_pool = self.env['operating.unit'].search([])
            self.planned_amount = self.env['bottom.line.budget.line'].search(
                [('bottom_line_account_id', '=', self.account_id.id)]).planned_amount
            line_planned_amount = self.planned_amount / len(op_pool)
            for obj in op_pool:
                vals.append((0, 0, {'account_id': self.account_id.id,
                                    'operating_unit_id': obj.id,
                                    'planned_amount': line_planned_amount,
                                    }))
            self.branch_budget_lines = vals


class BudgetBranchDistributionLine(models.Model):
    _name = "budget.branch.distribution.line"
    _description = "Budget Branch Distribution Line"

    branch_budget_id = fields.Many2one('budget.branch.distribution',string='Budget')
    account_id = fields.Many2one('account.account',string='Accounts')
    operating_unit_id = fields.Many2one('operating.unit', string='Branch')
    planned_amount = fields.Float('Planned Amount', required=True)