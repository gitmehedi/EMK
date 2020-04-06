from odoo import api, fields, models, _


class AccountTax(models.Model):
    _inherit = 'account.tax'

    raw_amount = fields.Float(string='Amount', required=True, digits=(16, 4))
    is_reverse = fields.Boolean(string='Is Reverse?')
    amount = fields.Float(required=True, digits=(16, 4), compute='_compute_amount')

    @api.depends('raw_amount')
    def _compute_amount(self):
        if self.is_reverse:
            self.amount = self.raw_amount * -1
        else:
            self.amount = self.raw_amount



