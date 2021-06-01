from odoo import models, fields, api, _


class AccountAccountType(models.Model):
    _inherit = 'account.account.type'

    cost_center_required_on_journal = fields.Boolean(string='Cost Center Is Required On Journal Entry')
