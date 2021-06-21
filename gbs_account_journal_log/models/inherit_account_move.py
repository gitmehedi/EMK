from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class InheritAccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'mail.thread']

    @api.multi
    def _get_default_journal(self):
        res = super(InheritAccountMove, self)._get_default_journal()
        return res

    state = fields.Selection(track_visibility='onchange')
    date = fields.Date(required=True, states={'posted': [('readonly', True)]}, index=True,
                       default=fields.Date.context_today, track_visibility='onchange')
    journal_id = fields.Many2one('account.journal', string='Journal', required=True,
                                 states={'posted': [('readonly', True)]}, default=_get_default_journal, track_visibility='onchange')

    @api.multi
    def button_cancel(self):
        for move in self:
            if not move.journal_id.update_posted:
                raise UserError(_(
                    'You cannot modify a posted entry of this journal.\nFirst you should set the journal to allow cancelling entries.'))
        if self.ids:
            self.check_access_rights('write')
            self.check_access_rule('write')
            self._check_lock_date()
            self.write({'state': 'draft'})
            self.invalidate_cache()
        self._check_lock_date()
        return True
