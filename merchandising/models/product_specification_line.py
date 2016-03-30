from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator


class ProductSpecificationLine(models.Model):
    _name = 'product.specification.line'
    
    # Requied and Optional Fields
    remarks = fields.Text(string="Remarks", size=50)
    
    # Model Relationship
    
    part_id = fields.Many2one('product.part', string="Sketch Key/Part", required=True)
    style_id = fields.Many2one('product.style', string='Styles')
    spec_ids = fields.Many2many(comodel_name='product.specification',relation="pro_spec_line_relate_pro_spec", string='Specification')
   
    
    



     
    
    


        
        
            
    
