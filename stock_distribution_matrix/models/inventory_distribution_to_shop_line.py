from openerp import  fields, models

class inventory_distribution_to_shop_line(models.Model):
    _name = 'stock.distribution.to.shop.line'
    
    stock_distributions_id = fields.Many2one('stock.distribution.to.shop',string='Stock Distribution Detail')
    product_id = fields.Many2one('product.product',string='Product')
    on_hand_qty = fields.Float(string='On Hand Qty')
    source_location_id = fields.Many2one('stock.location',string='Source Location')
    target_location_id = fields.Many2one('stock.location',string='Target Location')
    pos_shop_id = fields.Many2one('pos.config',string='Shop')
    distribute_qty = fields.Float(string='Distribution Qty')