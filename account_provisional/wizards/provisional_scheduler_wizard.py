from odoo import models, fields, api, _
from odoo.exceptions import Warning


class ProvisionalSchedulerWizard(models.TransientModel):
    _name = 'provisional.scheduler.wizard'

    date_selection = fields.Date('Select Date',default=fields.Date.context_today)

    def action_provisional_scheduler(self):
        account_move_pool = self.env['account.move']
        return account_move_pool.action_create_provisional_journal(self.date_selection)

    def action_provisional_reverse(self):
        account_move_pool = self.env['account.move']
        return account_move_pool.action_reverse_provisional_journal(self.date_selection)