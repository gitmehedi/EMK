from openerp import api, models, fields


class StockTransferRequestLine(models.Model):
    _name = 'stock.transfer.request.line'


    quantity = fields.Integer(string="Quantity", required=True)

    """ Relational Fields """
    stock_transfer_id = fields.Many2one('stock.transfer.request')
    product_id = fields.Many2one('product.product', string="Product", required=True, ondelete="cascade")



