from odoo import api, fields, models, _


class AccountTax(models.Model):
    _inherit = 'account.tax'

    rebate = fields.Boolean(string='Rebate', default=False, readonly=True, states={'draft': [('readonly', False)]})
    rebate_account_id = fields.Many2one('account.account', string='Rebate Account', readonly=True, states={'draft': [('readonly', False)]})