# imports of odoo
from odoo import fields, models, api, _


class InheritedAccountAccount(models.Model):
    _inherit = "account.account"

    analytic_account_required = fields.Boolean(string='Is Analytic Acc Req on Bills?', default=False, track_visibility='onchange')
    cost_center_required = fields.Boolean(string='Is Cost Center Req on Bills?', default=False,
                                               track_visibility='onchange')

