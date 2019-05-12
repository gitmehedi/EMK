from odoo import api, fields, models, _

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

