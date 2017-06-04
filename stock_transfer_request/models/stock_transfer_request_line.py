from openerp import api, models, fields


class StockTransferRequestLine(models.Model):
    """
    Specify quantity when send to other shop
    """
    _name = 'stock.transfer.request.line'


    quantity = fields.Integer(string="Quantity", required=True)
    receive_quantity = fields.Integer(string="Receive Quantity")
    is_transfer = fields.Boolean(string="Is Transfer", default=False)
    is_receive= fields.Boolean(string="Is Receive", default=False)

    """ Relational Fields """
    stock_transfer_id = fields.Many2one('stock.transfer.request')
    product_id = fields.Many2one('product.product', string="Product", required=True, ondelete="cascade")



