from odoo import api, fields, models

class SalePriceChange(models.Model):
    _name = 'product.sale.history.line'
    _description = "Sale Price History"

    product_id = fields.Many2one('product.product', string="Product", required=True, domain=[('sale_ok', '=', True)],ondelete='cascade')
    list_price = fields.Float(string='Old Price', related='product_id.list_price', readonly=True)
    new_price = fields.Float(string='New Price', required=True)

    ## Relational fields
    sale_price_history_id = fields.Many2one('sale.price.change', 'id', ondelete='cascade')


