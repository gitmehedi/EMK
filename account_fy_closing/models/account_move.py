from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    is_opening = fields.Boolean(string='Is Opening', default=False, required=False)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    is_opening = fields.Boolean(string='Is Opening', default=False, required=False)
    is_profit = fields.Boolean(string='Is Profit', default=False)
