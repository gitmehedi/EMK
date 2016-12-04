from openerp import api, fields, models

class InheritedAccount(models.Model):
    _inherit = 'account.journal'
     
    is_redemption = fields.Boolean(string='Redemption Point', default=False)
    
    