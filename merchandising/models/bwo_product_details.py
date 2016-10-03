from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator
from string import digits


class BwoProductDetails(models.Model):
    _name = 'bwo.product.details'
    
    # Buyer Work Order fields
    qty = fields.Float(string='Order Quantity', required=True)
    status = fields.Boolean(string='Status')
    rate = fields.Float(string='Rate', digits=(15, 2))
    
    # Relationship fields
    product_id = fields.Many2one('product.product', string="Product", required=True)  
    uom_id = fields.Many2one('product.uom', string="UoM", ondelete='set null', required=True,
                             domain=[('category_id', '=', 'Unit')])
    bwo_details_id = fields.Many2one('buyer.work.order')
    
    # variable
    getData = []
    
    
    @api.multi
    def _validate_data(self, value):
        msg , filterInt = {}, {}
        
        filterInt['Order Quantity'] = value.get('qty', False)
        filterInt['Rate'] = value.get('rate', False)
        
        msg.update(validator._validate_number(filterInt))
        validator.validation_msg(msg)
        
        return True
    
    # All function which process data and operation
    @api.model
    def create(self, vals):
        self._validate_data(vals)
        
        return super(BwoProductDetails, self).create(vals)    
    
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        
        return super(BwoProductDetails, self).write(vals)  
    
    @api.onchange('qty')
    def onchange_qty(self):
        self.qty = self.qty
        
#     @api.model
#     def _get_product(self):
#         return 'fasdfsad' 
       
#     @api.onchange('product_id')
#     def onchange_product_id(self):
#         res = {'domain': {'product_id': []}}
#          
#         if self.product_id:
#             self.getData.append(self.product_id.id)
#              
#             prod_data = list(set(self.getData).symmetric_difference(self.product_id.product_tmpl_id.product_variant_ids.ids))
#             res['domain'] = {
#                 'product_id': [('id', 'in', prod_data)]
#             } 
#              
#             return res
     
    
    



     
    
    


        
        
            
    
