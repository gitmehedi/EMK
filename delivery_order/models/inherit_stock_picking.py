from odoo import api, fields, models

class InheritStockPicking(models.Model):
    _inherit = 'stock.picking'

    delivery_address = fields.Char('Delivery Address', compute='_get_delivery_address', readonly=False)

    @api.multi
    def _get_delivery_address(self):
        for stock in self:
            if stock.sale_id.partner_shipping_id:
                stock.delivery_address = stock.sale_id.partner_shipping_id.name
            else:
                stock.sale_id.partner_shipping_id = ''
