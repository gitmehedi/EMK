from odoo import api, fields, models
from odoo.exceptions import ValidationError


class InheritAccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    @api.multi
    def action_statement_print(self):
        return self.env['report'].get_action(self,
                                             report_name='gbs_samuda_petty_cash.petty_cash_report_xlsx')

    @api.constrains('balance_start')
    def _check_balance_start_negative_val(self):
        if self.balance_start < 0:
            raise ValidationError('Starting Balance can not be Negative')

    @api.constrains('balance_end_real')
    def _check_balance_end_real_negative_val(self):
        if self.balance_end_real < 0:
            raise ValidationError('Ending Balance can not be Negative')


