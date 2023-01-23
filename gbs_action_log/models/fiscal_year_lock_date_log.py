from odoo import fields, models, api, _
from datetime import datetime
from datetime import timedelta


class FiscalYearLockDateLog(models.Model):
    _name = 'fiscal.year.lock.date.log'
    _order = 'create_date DESC'


    period_lock_date = fields.Date(string="Non-Advisers Lock Date", required=True)
    fiscal_year_lock_date = fields.Date(string="Advisor Lock Date", required=True)
    modified_id = fields.Many2one('res.users', 'Modified By', index=True, readonly=True)
    modified_date = fields.Datetime(string="Date", required=True)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.multi
    def execute(self):
        if self.env.context.get('active_model', False) == 'account.config.settings' and \
                self.env.user.has_group('gbs_application_group.group_account_closing'):

            # Update the properties of res.company model
            current_date_time = datetime.now()
            current_date_time = current_date_time.strftime('%Y-%m-%d %H:%M:%S')
            self.env['fiscal.year.lock.date.log'].create({
                'period_lock_date': self.period_lock_date,
                'fiscal_year_lock_date': self.fiscalyear_lock_date,
                'modified_id': self.env.user.id,
                'modified_date': current_date_time,
            })
            return super(ResConfigSettings, self).execute()
        else:
            return super(ResConfigSettings, self).execute()
