from odoo import api, fields, models,_


class InheritResCompany(models.Model):
    _inherit='res.company'


    commission_journal = fields.Many2one('account.journal', string='Commission Journal')
    cash_suspense_account = fields.Many2one('account.account', string='Cash Sale Clearing A/C', required=False)

