from openerp import api, fields, models

class InheritedResPartner(models.Model):
    _inherit = 'res.partner' 
    
    last_purchase_point = fields.Float(string='Last Purchase Point', digits=(20, 2))
    point_loyalty = fields.Float(string='Loyalty Point', digits=(20, 2))
