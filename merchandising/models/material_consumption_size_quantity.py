from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator

class MaterialConsumptionSizeQuantity(models.Model):
    _name = 'material.consumption.size.quantity'
    
    quantity = fields.Integer(string='Quantity', size=30, required=True)
    
    # Model Constraints
    attr_size_id = fields.Many2one('product.attribute.value', string='Size', required=True
                                   , ondelete="cascade")
    yarn_acc_id = fields.Many2one('material.consumption.details', ondelete="cascade")
    
#     domain=[('attribute_id', '=', self.get_size_attr)]
    # All function which process data and operation
   
    @api.multi
    def _validate_data(self, value):
        msg , filterInt = {}, {}
        filterInt['Quantity'] = value.get('quantity', False)
       
        msg.update(validator._validate_number(filterInt))
        validator.validation_msg(msg)
        
        return True
    
    
    @api.model
    def create(self, vals):
        self._validate_data(vals)
        return super(MaterialConsumptionSizeQuantity, self).create(vals)
   
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        return super(MaterialConsumptionSizeQuantity, self).write(vals)
    
    def get_size_attr(self):
        attr_obj = self.env['product.attribute'].search([('is_size', '=', True)])
        
        if attr_obj:
            return attr_obj.id
        else:
            raise exceptions.ValidationError(validator.msg['size_attr'])
         
    
    @api.onchange('attr_size_id')
    def _onchange_attr_size_id(self):
        res = {}
        
        res['domain'] = {'attr_size_id': [('attribute_id', '=', self.get_size_attr())]}
        return res
 
        
    
    
    
    
   

