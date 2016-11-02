from openerp import api, exceptions, fields, models

class GoodsReceiveMatrixLine(models.Model):
    _name = 'goods.receive.matrix.line'

    """ Required and Optional Fields """

    product_uom_id = fields.Integer(string='UOM', size=40)
    product_qty = fields.Float(digits=(5, 2), string='Qty', size=20)

    """ Relational Fields """
    product_id = fields.Many2one('product.product', string="Product")
    matrix_id = fields.Many2one('goods.receive.matrix', string="Product Matrix")
    size_variant_id=fields.Many2one('product.attribute.value')
    color_variant_id=fields.Many2one('product.attribute.value')
