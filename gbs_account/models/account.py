# imports of odoo
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

class AccountAccount(models.Model):
    _inherit = "account.account"

    open_journal_entry = fields.Boolean(string='Allow Open Journal Entry', default=True)

    @api.onchange('user_type_id')
    def onchange_user_type_id(self):
        for rec in self:
            if self._origin.id:
                acc_move_line = self.env['account.move.line'].search([('account_id', '=', self._origin.id)])
                view_type_account = self.env['account.account.type'].search([('type', '=', 'view')], limit=1)

                if rec.user_type_id.id == view_type_account.id and acc_move_line:
                    raise UserError(_("You cannot change account type because this account has journal entries!"))


