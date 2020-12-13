# imports of odoo
from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    standard_qty = fields.Float(string='Standard Quantity', required=True, readonly=True)

    @api.multi
    def _create_extra_move(self):
        extra_move = super(StockMove, self)._create_extra_move()
        product_uom_qty = extra_move.product_uom_qty
        extra_move.write({'standard_qty': product_uom_qty})

        return extra_move
