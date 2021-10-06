from odoo import fields, models, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pack_type = fields.Many2one('product.packaging.mode', domain=[('is_deprecated', '=', False)])


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_id = fields.Many2one('product.product', string='Product',
                                 domain=[('sale_ok', '=', True), ('is_deprecated', '=', False)])
