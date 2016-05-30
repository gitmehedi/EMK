from openerp import models, fields, api, exceptions
from email import _name
from Crypto.Util.number import size

class ChecklistType(models.Model):
    _name='hr.exit.checklist.type'
    
    #Database fields
    code=fields.Char(string='Code', size=50, help='Please enter code.')
    name=fields.Char(string='Name', size=100, required=True, help='Please enter name.')
    description=fields.Text(string='Description', size=500, help='Please enter description')
    is_active=fields.Boolean(string='Active', default=True)