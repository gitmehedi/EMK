from odoo import api, fields, models, _
from odoo.exceptions import UserError

# ---------------------------------------------------------
# Bottom Line Budgets
# ---------------------------------------------------------
class BottomLineBudgetTemp(models.Model):
    _name = "bottom.line.budget.temp"
    _inherit = ['mail.thread']
    _order = "name"
    _description = "Bottom Line Budgetary Template"

    name = fields.Char('Name',required=True, size=50, track_visibility='onchange')
    date_create = fields.Datetime('Date', readonly=True, default=lambda self: fields.Datetime.now())
    bottom_line_budgets = fields.One2many('bottom.line.budget.temp.line', 'bottom_line_budget',
                                           string='Bottom Lines')

    @api.multi
    def action_select_accounts(self):
        res = self.env.ref('gbs_account_budget.view_bottom_line_wizard_form')

        result = {'name': _('Bottom Line'),
                  'view_type': 'form',
                  'view_mode': 'form',
                  'view_id': res and res.id or False,
                  'res_model': 'bottom.line.wizard',
                  'type': 'ir.actions.act_window',
                  'target': 'new',
                  'nodestroy': True,
                  }

        return result


class BottomLineBudgetTempLine(models.Model):
    _name = "bottom.line.budget.temp.line"
    _description = "Bottom Line Budgetary Template"

    bottom_line_budget = fields.Many2one('bottom.line.budget.temp',string='Bottom line budget')
    top_line_account_id = fields.Many2one('account.account',string='Top Line Accounts',
                                           domain=[('user_type_id', '=', 'View Type')])
    bottom_line_account_id = fields.Many2one('account.account',string='Bottom Line Accounts',
                                              domain=[('user_type_id', '!=', 'View Type')])