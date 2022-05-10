from odoo import fields, models, api
from datetime import datetime


class AnalyticAccountWizard(models.TransientModel):
    _name = 'analytic.account.selection.wizard'

    analytic_account = fields.Many2one('account.analytic.account', string='Analytic Account', required=True)
    expense_type = fields.Many2one(
        comodel_name='purchase.expense.type', string='Expense type',
        required=True)
    ref = fields.Char(string="Reference")

    @api.multi
    def action_import(self):
        used_context = dict()
        journal_ids = self.env['account.journal'].search([('type', '!=', 'situation')])
        used_context['journal_ids'] = journal_ids.ids or False
        used_context['state'] = 'all'
        used_context['strict_range'] = True
        used_context['date_from'] = datetime.now().date().replace(month=1, day=1)
        used_context['date_to'] = datetime.now().date().replace(month=12, day=31)
        used_context['analytic_account_ids'] = self.analytic_account
        #  accounts_result = self._get_account_move_entry(used_context)
        accounts_result = self.env['accounting.report.utility']._get_account_move_entry(False, used_context)

        for account in accounts_result:
            if account['closing_balance'] != 0:
                lc_pad_account = self.env['ir.values'].get_default('account.config.settings', 'lc_pad_account')
                if lc_pad_account != account['account_id']:
                    self.env['purchase.cost.distribution.expense'].create({
                        'distribution': self.env.context['active_id'],
                        'ref': self.ref,
                        'expense_amount': account['closing_balance'],
                        'type': self.expense_type.id,
                        'account_id': account['account_id']
                    })

        if 'active_id' in self.env.context:
            distribution = self.env['purchase.cost.distribution'].browse(self.env.context['active_id'])
            distribution.write({'analytic_account': self.analytic_account.id})

    def action_cancel(self):
        """ close wizard"""
        return {'type': 'ir.actions.act_window_close'}
