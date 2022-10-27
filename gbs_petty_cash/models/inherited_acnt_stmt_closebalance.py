from odoo import fields, models, api


class InheritedAccountBankStmtCloseCheck(models.TransientModel):
    _inherit = 'account.bank.statement.closebalance'

    @api.multi
    def validate(self):
        bnk_stmt_id = self.env.context.get('active_id', False)
        if bnk_stmt_id:
            if self.env['account.bank.statement'].browse(bnk_stmt_id).is_petty_cash_journal:
                self.env['account.bank.statement'].browse(bnk_stmt_id).button_confirm_bank_duplicate()
            else:
                self.env['account.bank.statement'].browse(bnk_stmt_id).button_confirm_bank()
        return {'type': 'ir.actions.act_window_close'}
