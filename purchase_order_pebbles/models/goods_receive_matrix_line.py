from openerp import api, exceptions, fields, models
from datetime import date
from openerp.exceptions import Warning

class GoodsReceiveMatrixLine(models.Model):
    _name = 'goods.receive.matrix.line'

    product_id = fields.Many2one('product.product', 'Product')
    product_qty = fields.Float(digits=(5, 2), string='Qty', size=20)
    matrix_id = fields.Many2one('goods.receive.matrix', 'Product Matrix')
#     color_attribute_id = fields.Many2one('product.attribute', string='Color Attribute')
#     color_value_id = fields.Many2one('product.attribute.value', string='Color')
#     size_attribute_id = fields.Many2one('product.attribute', string='Size Attribute')
#     size_value_id = fields.Many2one('product.attribute.value', string='Size')
    product_uom_id = fields.Integer(string='UOM', size=40)
    
    size_variant_id=fields.Many2one(comodel_name='product.custom.variant')
    other_variant_id=fields.Many2one(comodel_name='product.custom.variant')

    