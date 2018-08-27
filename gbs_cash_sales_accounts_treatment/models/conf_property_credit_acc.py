from odoo import models, fields, api


class ConfPopertyCreditAcc(models.Model):
    _name = 'conf.credit.acc'
    _description = 'Cash Payment Terms line'


    cash_suspense_account = fields.Many2one('account.account', string='Cash Suspense A/C', required=True)


