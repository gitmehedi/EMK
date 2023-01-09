# imports of odoo
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class AccountAccount(models.Model):
    _inherit = "account.account"

    is_control_account = fields.Boolean(string='Is Control Account', default=False)

    open_journal_entry = fields.Boolean(string='Allow Open Journal Entry', default=True)

    @api.multi
    def write(self, values):
        if 'user_type_id' in values:
            account_type = self.env['account.account.type'].browse(values['user_type_id'])
            # if wants to convert to view type
            if account_type.type == 'view':
                # if move lines exist
                acc_move_line = self.env['account.move.line'].search([('account_id', '=', self.id)])
                if len(acc_move_line) > 0:
                    raise UserError(_('''You cannot change account type to 'View Type' because this account has journal entries!'''))

        res = super(AccountAccount, self).write(values)
        return res

