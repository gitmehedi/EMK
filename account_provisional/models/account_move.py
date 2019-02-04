from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
