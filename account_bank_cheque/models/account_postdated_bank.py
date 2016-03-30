from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator


class BankEntry(models.Model):
    _name = 'account.postdated.bank'
    
    # database fields
    code = fields.Char(string='Code', size=10, help='Please enter bank code.')
    name = fields.Char(string='Name of Bank', required=True, size=100, help='Please enter bank name.')
    