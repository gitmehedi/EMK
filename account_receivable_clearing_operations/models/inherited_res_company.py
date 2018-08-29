from odoo import api, fields, models,_


class InheritResCompany(models.Model):
    _inherit='res.company'


    cash_clearing_account = fields.Many2one('account.account', string='Cash Clearing A/C', required=False)

