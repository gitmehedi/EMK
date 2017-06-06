from openerp import api, models, fields


class StockTransferRequestLine(models.Model):
    """
    Specify quantity when send to other shop
    """
    _name = 'stock.transfer.request.line'


    store_qty = fields.Integer(string="Store Qty", readonly=True)
    quantity = fields.Integer(string="Quantity", required=True)
    receive_quantity = fields.Integer(string="Receive Quantity")

    """ Relational Fields """
    stock_transfer_id = fields.Many2one('stock.transfer.request')
    product_id = fields.Many2one('product.product', string="Product", required=True, ondelete="cascade")

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            if self.stock_transfer_id.state=='transfer':
                quant = self.env['stock.quant'].search([('product_id', '=', self.product_id.id),
                                                        ('location_id', '=', self.stock_transfer_id.to_shop_id.id)])
            else:
                quant = self.env['stock.quant'].search([('product_id', '=', self.product_id.id),
                                                        ('location_id', '=', self.stock_transfer_id.requested_id.id)])

            self.store_qty = sum([val.qty for val in quant])

    @api.onchange('quantity')
    def onchange_quantity(self):
        if self.product_id:
            if self.store_qty < self.quantity:
                self.quantity = self.store_qty









