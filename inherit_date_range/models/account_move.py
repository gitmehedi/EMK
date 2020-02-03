from odoo import api, fields, models, SUPERUSER_ID


class AccountMove(models.Model):
    _inherit = "account.move"

    is_opening = fields.Boolean(string='Is Opening', default=False)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    is_opening = fields.Boolean(string='Is Opening', default=False)
    is_profit = fields.Boolean(string='Is Profit', default=False)