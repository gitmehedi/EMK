from odoo import fields, models,_


class InheritResCompany(models.Model):
    _inherit='res.company'

    account_receive_clearing_acc = fields.Many2one('account.account',string='Account Receive Clearing A/C', required=False)
    journal_id = fields.Many2one('account.journal', string='Account Receive Journal')
