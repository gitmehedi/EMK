
from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp

class AccountAccount(models.Model):
    _inherit = "account.account"

    @api.multi
    @api.depends('move_line_ids','move_line_ids.amount_currency','move_line_ids.debit','move_line_ids.credit')
    def compute_values(self):
        return