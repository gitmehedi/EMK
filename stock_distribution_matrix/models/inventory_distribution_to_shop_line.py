from openerp import fields, models, api


class InventoryDistributionToShopLine(models.Model):
    _name = 'stock.distribution.to.shop.line'

    on_hand_qty = fields.Float(string='On Hand Qty')
    distribute_qty = fields.Float(string='Distribution Qty')

    """ Realtional Fields """
    stock_distributions_id = fields.Many2one('stock.distribution.to.shop', string='Stock Distribution Detail',
                                             ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product')
    source_location_id = fields.Many2one('stock.location', string='Source Location')
    target_location_id = fields.Many2one('stock.location', string='Target Location')
    pos_shop_id = fields.Many2one('pos.config', string='Shop')

    state = fields.Selection([
        ('draft', 'Waiting'),
        ('confirm', 'Confirm'),
        ('prepare', 'Prepare'),
        ('transfer', 'Transfer'),
    ], string='Status', default='draft', states={'draft': [('readonly', False)]})

