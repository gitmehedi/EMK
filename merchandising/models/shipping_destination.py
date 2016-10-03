from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator


class ShippingDestination(models.Model):
    _name = 'shipping.destination'
    
    # Shipping Destination Fields
    name = fields.Char(string="Destination", size=30, required=True)
    
    # Relationship fields
    country_id = fields.Many2one('res.country', string='Country', required=True)
    
    
    # All function which process data and operation
    
    
    @api.multi
    def _validate_data(self, value):
        msg , filterChar = {}, {}
        
        filterChar['Destination'] = value.get('name', False)
        
        msg.update(validator._validate_character(filterChar, True))
        validator.validation_msg(msg)
        
        return True
    
    
    @api.model
    def create(self, vals):
        self._validate_data(vals)
        vals['name'] = vals.get('name', False).strip()
        
        return super(ShippingDestination, self).create(vals)
    
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        
        if vals.get('name', False):
            vals['name'] = vals.get('name', False).strip()
        
        return super(ShippingDestination, self).write(vals)
    

    
    
    
    



     
    
    


        
        
            
    
