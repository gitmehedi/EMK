from odoo import api, fields, models, _
from odoo.exceptions import Warning, ValidationError


class AccountAccount(models.Model):
    _inherit = 'account.account'

    # new field
    revaluation = fields.Boolean(string='Allow Revaluation', default=False, track_visibility='onchange')

    @api.constrains('currency_id')
    def _constrains_currency_id(self):
        if self.currency_id.id == self.env.user.company_id.currency_id.id:
            raise ValidationError(_("Account Currency and Company Currency can not be same."))
