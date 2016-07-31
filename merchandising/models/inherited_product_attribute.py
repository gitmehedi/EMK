from openerp import api, fields, models

class InheritedProductAttribute(models.Model):
    _inherit = 'product.attribute'
    
    is_color = fields.Boolean(string="Color", default=False) 
    is_size = fields.Boolean(string="Size", default=False)
    

