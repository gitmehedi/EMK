from openerp import models, fields, api
from openerp.addons.helper import validator

class ResRegion(models.Model):
    _name = 'res.region'
    
    name = fields.Char(string='Name', size=30, required=True, empty=False)
    country_ids = fields.Many2many('res.country', string='Countries')
    active = fields.Boolean(default=True)
    
    
    _sql_constraints = [
        ('region_name_uniq', 'unique(name)', validator.msg['unique'])
    ]
    # All functions
    
    @api.multi
    def _validate_data(self, value):
        msg , filterChar = {}, {}
        
        filterChar['Name'] = value.get('name', False)
        
        msg.update(validator._validate_character(filterChar,True))
        validator.validation_msg(msg)
        
        return True
    
    
    @api.model
    def create(self, vals):
        self._validate_data(vals)
        vals['name'] = vals.get('name', False).strip()
        
        return super(ResRegion, self).create(vals)
    
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        
        if vals.get('name', False):
            vals['name'] = vals.get('name', False).strip()
        
        return super(ResRegion, self).write(vals)
    
   

