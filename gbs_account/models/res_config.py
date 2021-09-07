from odoo import models, fields, api


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    def _get_default_period_lock_date(self):
        return self.env.user.company_id.period_lock_date

    def _get_default_fiscalyear_lock_date(self):
        return self.env.user.company_id.fiscalyear_lock_date

    period_lock_date = fields.Date(default=lambda self: self._get_default_period_lock_date())
    fiscalyear_lock_date = fields.Date(default=lambda self: self._get_default_fiscalyear_lock_date())


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.multi
    def execute(self):
        if self.env.context.get('active_model', False) == 'account.config.settings' and \
                self.env.user.has_group('gbs_application_group.group_account_closing'):

            # Update the properties of res.company model
            query = """ UPDATE res_company SET period_lock_date=%s, fiscalyear_lock_date=%s WHERE id=%s """
            self._cr.execute(query, tuple([self.period_lock_date, self.fiscalyear_lock_date, self.env.user.company_id.id]))

            # force client-side reload (update user menu and current view)
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        else:
            return super(ResConfigSettings, self).execute()
