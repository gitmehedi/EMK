from openerp import models, fields

class product_style_line(models.Model):
    _name = 'product.style.line'
    
    style_id = fields.Many2one('product.style', string="Style", required=True, ondelete="cascade")  
    size_group_id = fields.Many2one('product.size.group', string="Size Group", required=True)  
    size_id = fields.Many2one('product.size',string="Code")
    
    

