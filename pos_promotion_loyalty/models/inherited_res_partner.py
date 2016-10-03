from openerp import api, fields, models

class InheritedResPartner(models.Model):
    _inherit = 'res.partner' 
    
    point_loyalty = fields.Float(string='Loyalty Point', digits=(20,2))
