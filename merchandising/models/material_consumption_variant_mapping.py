from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator

class MaterialConsumptionVariantMapping(models.Model):
    _name = 'material.consumption.variant.mapping'
    
    
    # Model Constraints
    attr_size_id = fields.Many2one('product.attribute.value', string='Size', required=True, ondelete="cascade")
   
    prod_variant_ids = fields.Many2many(comodel_name='product.attribute.value',
                        relation='prod_attr_mat_cons_mapping_rel_relationsla',
                        column1='mcvm_id',
                        column2='attr_id', string='Variants', required=True)
    yarn_acc_mapping_id = fields.Many2one('material.consumption.details', ondelete="cascade")
    

    # All function which process data and operation
   
    
    
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
 
        
    
    
    
    
   

