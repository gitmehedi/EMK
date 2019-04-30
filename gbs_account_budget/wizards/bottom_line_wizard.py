from odoo import api, fields, models, _

class BottomLineWizard(models.TransientModel):
    _name = 'bottom.line.wizard'

    top_line_budget_line = fields.Many2one('top.line.budget.lines', 'Top line Budget', required=True)

    bottom_line_accounts = fields.One2many('bottom.line.accounts.wizard', 'bottom_line_account_ids', string='Bottom Lines')

    @api.onchange('top_line_budget_line')
    def onchange_top_line_budget_line(self):
        if self.top_line_budget_line:
            self.bottom_line_accounts = []
            vals = []
            accounts_pool = self.env['account.account'].search([('id', '=', self.top_line_budget_line.account_id.id)])
            for obj in accounts_pool:
                vals.append((0, 0, {'top_line_account_ids': self.top_line_budget_line.account_id.id,
                                    'bottom_line_account_ids': obj.id,
                                    }))
            self.product_lines = vals

class BottomLineAccountsWizard(models.TransientModel):
    _name = 'bottom.line.accounts.wizard'

    bottom_line_account_ids = fields.Many2one('bottom.line.wizard', string='Bottom Line Accounts')
    top_line_account_id = fields.Many2one('account.account', string='Top Line Accounts',
                                           domain=[('user_type_id', '=', 'View Type')])
    bottom_line_account_id = fields.Many2one('account.account', string='Bottom Line Accounts',
                                              domain=[('user_type_id', '!=', 'View Type')])
