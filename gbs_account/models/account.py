# imports of odoo
from odoo import fields, models, api, _


class AccountAccount(models.Model):
    _inherit = "account.account"

    open_journal_entry = fields.Boolean(string='Allow Open Journal Entry', default=True)
