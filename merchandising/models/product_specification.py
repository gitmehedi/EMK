from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator


class ProductSpecification(models.Model):
    _name = 'product.specification'
    
    # Requied and Optional Fields
    name = fields.Char(size=30, string="Name")
    active = fields.Boolean(default=True)
   
   
    # All functions
    
    @api.multi
    def _validate_data(self, value):
        msg , filterChar = {}, {}
        
        filterChar['Name'] = value.get('name', False)
        
        msg.update(validator._validate_character(filterChar))
        validator.validation_msg(msg)
        
        return True
    
    
    @api.model
    def create(self, vals):
        self._validate_data(vals)
        vals['name'] = vals.get('name', False).strip()
        
        return super(ProductSpecification, self).create(vals)
    
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        
        if vals.get('name', False):
            vals['name'] = vals.get('name', False).strip()
        
        return super(ProductSpecification, self).write(vals)
  
    
    



     
    
    


        
        
            
    
