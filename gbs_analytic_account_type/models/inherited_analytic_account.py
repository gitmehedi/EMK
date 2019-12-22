from odoo import api, fields, models, _


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    type = fields.Selection([('cost', 'Cost'), ('profit', 'Profit')], string='Type')
