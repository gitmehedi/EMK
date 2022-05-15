# imports of odoo
from odoo import fields, models, api, _


class InheritedAccountAccount(models.Model):
    _inherit = "account.account"

    analytic_account_required = fields.Boolean(string='Is Analytic Account Required?', default=False, track_visibility='always')
