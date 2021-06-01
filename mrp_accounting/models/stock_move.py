from collections import defaultdict

# imports of odoo
from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def product_price_update_(self):
        tmpl_dict = defaultdict(lambda: 0.0)
        # adapt standard price on incomming moves if the product cost_method is 'average'
        std_price_update = {}
        for move in self.filtered(lambda move: move.location_id.usage in ('production') and move.product_id.cost_method == 'average'):
            product_tot_qty_available = move.product_id.qty_available + tmpl_dict[move.product_id.id]

            # if the incoming move is for a purchase order with foreign currency, need to call this to get the same value that the quant will use.
            if product_tot_qty_available <= 0:
                new_std_price = move.get_price_unit()
            else:
                # Get the standard price
                amount_unit = std_price_update.get(
                    (move.company_id.id, move.product_id.id)) or move.product_id.standard_price
                new_std_price = ((amount_unit * product_tot_qty_available) + (
                            move.get_price_unit() * move.product_qty)) / (product_tot_qty_available + move.product_qty)

            tmpl_dict[move.product_id.id] += move.product_qty
            # Write the standard price, as SUPERUSER_ID because a warehouse manager may not have the right to write on products
            move.product_id.with_context(force_company=move.company_id.id).sudo().write(
                {'standard_price': new_std_price})
            std_price_update[move.company_id.id, move.product_id.id] = new_std_price
