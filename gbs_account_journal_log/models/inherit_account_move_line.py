from odoo import api, fields, models


class InheritAccountMoveLine(models.Model):
    _name = 'account.move.line'
    _inherit = ['account.move.line', 'mail.thread']

    debit = fields.Monetary(default=0.0, currency_field='company_currency_id', track_visibility='onchange')
    credit = fields.Monetary(default=0.0, currency_field='company_currency_id', track_visibility='onchange')
    account_id = fields.Many2one('account.account', string='Account', required=True, index=True,
                                 ondelete="cascade", domain=[('deprecated', '=', False)],
                                 default=lambda self: self._context.get('account_id', False), track_visibility='onchange')
