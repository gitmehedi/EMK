from openerp import api, models, fields


class StockRequisitionTransferLine(models.Model):
    """
    Specify quantity when send to other shop
    """
    _name = 'stock.requisition.transfer.line'


    store_qty = fields.Integer(string="Store Qty")
    quantity = fields.Integer(string="Quantity")
    receive_quantity = fields.Integer(string="Receive Quantity")

    """ Relational Fields """
    stock_requisition_id = fields.Many2one('stock.requisition.transfer')
    product_id = fields.Many2one('product.product', string="Product", required=True, ondelete="cascade")

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            if self.stock_requisition_id.state=='transfer':
                quant = self.env['stock.quant'].search([('product_id', '=', self.product_id.id),
                                                        ('location_id', '=', self.get_location(self.stock_requisition_id.to_shop_id.id))])
            else:
                quant = self.env['stock.quant'].search([('product_id', '=', self.product_id.id),
                                                        ('location_id', '=', self.get_location(self.stock_requisition_id.requested_id.id))])

            self.store_qty = sum([val.qty for val in quant])

    def get_location(self, operating_unit):
        location = self.env['pos.config'].search([('operating_unit_id', '=', operating_unit)])
        if location:
            return location[0].stock_location_id.id




