from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator

class InsuranceAgency (models.Model):
    _name = "insurance.agency"
    
    name = fields.Char(string="name", size=30, required=True)
    status = fields.Boolean(string="status", default=True)
    
    
     # All function which process data and operation
    @api.multi
    def _validate_data(self, value):
        msg , filterChar = {}, {}
        
        filterChar['Name'] = value.get('name', False)
        
        msg.update(validator._validate_character(filterChar, True))
        validator.validation_msg(msg)
        
        return True
    
    
    @api.model
    def create(self, vals):
        self._validate_data(vals)
        vals['name'] = vals.get('name', False).strip()
        
        return super(InsuranceAgency, self).create(vals)
    
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        
        if vals.get('name', False):
            vals['name'] = vals.get('name', False).strip()
        
        return super(InsuranceAgency, self).write(vals)
