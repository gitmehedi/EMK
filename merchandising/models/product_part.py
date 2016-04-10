from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator


class ProductPart(models.Model):
    _name = 'product.part'
    
    # Requied and Optional Fields
    name = fields.Char(size=30, string="Name")
    active = fields.Boolean(default=True)
    
    # Model Relationship
    spec_line_ids = fields.One2many('product.specification.line','part_id')
   
   
   
    # All functions
    
    @api.multi
    def _validate_data(self, value):
        msg , filterChar = {}, {}

        validator.validation_msg(msg)
        
        return True
    
    
    @api.model
    def create(self, vals):
        self._validate_data(vals)
        vals['name'] = vals.get('name', False).strip()
        
        return super(ProductPart, self).create(vals)
    
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        
        if vals.get('name', False):
            vals['name'] = vals.get('name', False).strip()
        
        return super(ProductPart, self).write(vals)
    
    
    
    



     
    
    


        
        
            
    
