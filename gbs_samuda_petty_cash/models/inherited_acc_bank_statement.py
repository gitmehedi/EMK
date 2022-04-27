from odoo import api, models


class InheritAccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    @api.multi
    def action_statement_print(self):
        return self.env['report'].get_action(self,
                                             report_name='gbs_samuda_petty_cash.petty_cash_report_xlsx')



