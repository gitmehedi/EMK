from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator

class MarginBuilt (models.Model):
    _name = "margin.built"
    
    name = fields.Char(string = "name")
    sn = fields.Integer(string="SN", default=True)
    account = fields.Char(string = "Account")
    fc_value = fields.Integer(string = "FC value")
    lc_value = fields.Integer(string = "LC value")
    exchange_rate = fields.Integer(string = "Exchange rate")
    
    
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
        
        return super(MarginBuilt, self).create(vals)
    
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        
        if vals.get('name', False):
            vals['name'] = vals.get('name', False).strip()
        
        return super(MarginBuilt, self).write(vals)
