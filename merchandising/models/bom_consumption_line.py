from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator

class BOMConsumptionLine(models.Model):
    _name = "bom.consumption.line"
    
    
    # Required and Optional Fields
    quantity = fields.Float(string="Quantity", digits=(10, 2), default=1.00, required=True)
    status = fields.Char(size=30, readonly=True)
    uom_category = fields.Integer(invisible=True)
    
    
    # Model Relationship
    product_id = fields.Many2one('product.product', string='Product', required=True) 
    
    uom_id = fields.Many2one('product.uom', string='UoM', required=True)
    preffered_supplier_id = fields.Many2one('res.partner', string="Preffered Supplier", readonly=True,
                                            domain=[('supplier', '=', 'True')])
    buyer_mentioned_supplier_id = fields.Many2one('res.partner', string="Buyer Mentioned Supplier",
                                            domain=[('supplier', '=', 'True')])
    
    mc_yarn_id = fields.Many2one('bom.consumption', ondelete="cascade")
    mc_acc_id = fields.Many2one('bom.consumption', ondelete="cascade")


    # All kinds of constraints
    
    @api.multi
    def _validate_data(self, value):
        msg , filterNum = {}, {}
        
        filterNum['Quantity'] = value.get('quantity', False)
        if filterNum['Quantity']:
            msg.update(validator._validate_number(filterNum))
            validator.validation_msg(msg)
        
        return True
    

    @api.model
    def create(self, vals):
        self._validate_data(vals)
        
        return super(BOMConsumptionLine, self).create(vals)
   
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        return super(BOMConsumptionLine, self).write(vals)
    
    
    # OnChange Handler
#     @api.onchange('product_id')
#     def _onchange_product_id(self):
#         pro_obj = self.env["product.product"]
#         uom_obj = self.env["product.uom"]
#         
#         if self.product_id.id:
#             
#             uom_ins = pro_obj.browse([self.product_id.id])
#             self.uom_category = uom_ins.uom_id.category_id.id
#             self.uom_id = uom_ins.uom_id.id
# 
#         return uom_obj
