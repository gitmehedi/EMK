from openerp import fields, models


class WarehouseToShopDistributionLine(models.Model):
    _name = 'warehouse.to.shop.distribution.line'
    _rec_name = 'product_id'
    _order = 'id desc'

    transfer_qty = fields.Float(string='Transfer Quantity', required=True)
    receive_qty = fields.Float(string='Receive Quantity')
    is_transfer = fields.Boolean(default=False)
    is_receive = fields.Boolean(default=False)

    """ Realtional Fields """
    warehouse_distribution_id = fields.Many2one('warehouse.to.shop.distribution', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', readonly=True, required=True, ondelete='cascade')
    product_uom_id = fields.Many2one('product.uom', string='UoM', readonly=True, required=True)
    stock_distribution_line_id = fields.Many2one('stock.distribution.to.shop.line', ondelete='cascade')
