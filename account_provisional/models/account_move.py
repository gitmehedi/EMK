from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"


    def action_create_provisional_journal(self):
        return True

    def action_reverse_provisional_journal(self):
        return True


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
