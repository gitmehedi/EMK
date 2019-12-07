from odoo import api, fields, models


class InheritAccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'mail.thread']

    @api.multi
    def _get_default_journal(self):
        res = super(InheritAccountMove, self)._get_default_journal()
        return res

    date = fields.Date(required=True, states={'posted': [('readonly', True)]}, index=True,
                       default=fields.Date.context_today, track_visibility='onchange')
    journal_id = fields.Many2one('account.journal', string='Journal', required=True,
                                 states={'posted': [('readonly', True)]}, default=_get_default_journal, track_visibility='onchange')
