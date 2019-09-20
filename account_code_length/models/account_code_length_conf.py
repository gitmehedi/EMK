from odoo import api, fields, models


class AccountCodeLength(models.Model):
    _name = "account.code.length"
    _rec_name='name'

    name = fields.Char(string='COA code Length', default='COA code Length')
    account_code_length = fields.Integer(string='Chart of Accounts Code Length', help='Determins length for Code in Chart of Account entry')

