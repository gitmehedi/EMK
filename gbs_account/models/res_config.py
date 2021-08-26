from odoo import models, fields, api


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    def _get_default_period_lock_date(self):
        return self.env.user.company_id.period_lock_date

    def _get_default_fiscalyear_lock_date(self):
        return self.env.user.company_id.fiscalyear_lock_date

    period_lock_date = fields.Date(default=lambda self: self._get_default_period_lock_date())
    fiscalyear_lock_date = fields.Date(default=lambda self: self._get_default_fiscalyear_lock_date())
