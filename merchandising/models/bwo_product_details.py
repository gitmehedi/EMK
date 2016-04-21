from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator
from string import digits


class BwoProductDetails(models.Model):
    _inherit = 'sale.order.line'

    name = fields.Char()
    qty = fields.Float(string='Order Quantity', required=True)
    status = fields.Boolean(string='Status')
    rate = fields.Float(string='Rate', digits=(15, 2))
    
    """ Relationship fields """
    product_id = fields.Many2one('product.product', string="Product", required=True)  
    # uom_id = fields.Many2one('product.uom', string="UoM", ondelete='set null', required=True,
    #                          domain=[('category_id', '=', 'Unit')])
    bwo_details_id = fields.Many2one('sale.order')
    


    @api.multi
    def _validate_data(self, value):
        msg , filterInt = {}, {}
        
        filterInt['Order Quantity'] = value.get('qty', False)
        filterInt['Rate'] = value.get('rate', False)
        
        msg.update(validator._validate_number(filterInt))
        validator.validation_msg(msg)
        
        return True

    
    """ All function which process data and operation """
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

     
    
    



     
    
    


        
        
            
    
