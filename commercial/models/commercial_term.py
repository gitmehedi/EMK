from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator


class CommercialTerm(models.Model):
    _name = 'commercial.term'
    
    # database fields
    name = fields.Char(string="Name", size=30, required=True)
    code = fields.Char(string="Code Name", size=30)
    status = fields.Boolean(string='Status', default=True)
    
    # Relationship fields
    
    
    
    # All function which process data and operation
    @api.multi
    def _validate_data(self, value):
        msg , filterChar = {}, {}
        
        filterChar['Name'] = value.get('name', False)
        filterChar['Code Name'] = value.get('code', False)
        
        msg.update(validator._validate_character(filterChar, True))
        validator.validation_msg(msg)
        
        return True
    
    
    @api.model
    def create(self, vals):
        # self._validate_data(vals)
        vals['name'] = vals.get('name', False).strip()
        vals['code'] = vals.get('code', False)
        
        return super(CommercialTerm, self).create(vals)
    
    @api.multi
    def write(self, vals):
        # self._validate_data(vals)
        
        if vals.get('name', False):
            vals['name'] = vals.get('name', False).strip()
            vals['code'] = vals.get('code', False)
        
        return super(CommercialTerm, self).write(vals)
    

    
    
    
    



     
    
    


        
        
            
    
