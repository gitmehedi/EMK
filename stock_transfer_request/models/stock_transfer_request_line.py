from openerp import api, models, fields


class StockTransferRequestLine(models.Model):
    """
    Specify quantity when send to other shop
    """
    _name = 'stock.transfer.request.line'

    store_qty = fields.Integer(string="Store Quantity", store=True)
    quantity = fields.Integer(string="Quantity", required=True)
    receive_quantity = fields.Integer(string="Receive Quantity")

    """ Relational Fields """
    stock_transfer_id = fields.Many2one('stock.transfer.request')
    product_id = fields.Many2one('product.product', string="Product", required=True, ondelete="cascade")

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            if self.stock_transfer_id.state=='transfer':
                location_id = self.env['pos.config'].search([('operating_unit_id', '=', self.stock_transfer_id.transfer_shop_id.id)])
                quant = self.env['stock.quant'].search([('product_id', '=', self.product_id.id),
                                                        ('location_id', '=', location_id[0].stock_location_id.id)])
            else:
                location_id = self.env['pos.config'].search(
                    [('operating_unit_id', '=', self.stock_transfer_id.my_shop_id.id)])
                quant = self.env['stock.quant'].search([('product_id', '=', self.product_id.id),
                                                        ('location_id', '=', location_id[0].stock_location_id.id)])

            self.store_qty = sum([val.qty for val in quant])

    @api.onchange('quantity')
    def onchange_quantity(self):
        if self.product_id:
            if self.store_qty < self.quantity:
                self.quantity = self.store_qty


    def get_location(self, operating_unit):
        location = self.env['pos.config'].search([('operating_unit_id', '=', operating_unit)])
        if location:
            return location[0].stock_location_id.id









