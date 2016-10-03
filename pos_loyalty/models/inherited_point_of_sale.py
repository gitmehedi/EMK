from openerp import api, fields, models

class InheritedPointOfSale(models.Model):
    _inherit = 'pos.category'
     
    loyalty_point = fields.Integer(string='Loyalty Point')
