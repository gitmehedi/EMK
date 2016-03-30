from openerp import fields, models

class ProductSizeLine(models.Model):
    _name = 'product.size.line'
    
    region_id = fields.Many2one('res.region',
        ondelete='set null', string="Region", index=True, required=True)
    remark = fields.Char(required=True)
    product_size_id = fields.Many2one('product.size',
       ondelete='set null', string="Product Size", index=True)
