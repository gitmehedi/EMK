from openerp import api, models, fields


class StockRequisitionTransferLine(models.Model):
    """
    Specify quantity when send to other shop
    """
    _name = 'stock.requisition.transfer.line'


    store_qty = fields.Integer(string="Store Qty", readonly=True)
    quantity = fields.Integer(string="Quantity", required=True)
    receive_quantity = fields.Integer(string="Receive Quantity")

    """ Relational Fields """
    stock_requisition_id = fields.Many2one('stock.requisition.transfer')
    product_id = fields.Many2one('product.product', string="Product", required=True, ondelete="cascade")

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            if self.stock_requisition_id.state=='transfer':
                quant = self.env['stock.quant'].search([('product_id', '=', self.product_id.id),
                                                        ('location_id', '=', self.stock_requisition_id.to_shop_id.id)])
            else:
                quant = self.env['stock.quant'].search([('product_id', '=', self.product_id.id),
                                                        ('location_id', '=', self.stock_requisition_id.requested_id.id)])

            self.store_qty = sum([val.qty for val in quant])

    @api.onchange('quantity')
    def onchange_quantity(self):
        if self.product_id:
            if self.store_qty < self.quantity:
                self.quantity = self.store_qty









