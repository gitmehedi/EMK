from collections import defaultdict

# imports of odoo
from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def product_price_update_before_done(self):

        # Start Custom Logic For GBS : Unit Price will not update for Foreign Purchase (LC & TT). Because landed cost are not added on PO

        for move in self.filtered(lambda move: move.location_id.usage in ('supplier', 'production') and move.product_id.cost_method == 'average'):

            po = self.env['purchase.order'].suspend_security().search([('name', '=', move.origin)], limit=1)
            if not po:
                return
            if po.region_type in ('foreign') or po.purchase_by in ('lc','tt'):
                return

            super(StockMove, self).product_price_update_before_done()

        # End Custom Logic For GBS



        # tmpl_dict = defaultdict(lambda: 0.0)
        # # adapt standard price on incomming moves if the product cost_method is 'average'
        # std_price_update = {}
        # for move in self.filtered(lambda move: move.location_id.usage in ('supplier', 'production') and move.product_id.cost_method == 'average'):
        #
        #     # Start Custom Logic For GBS : Unit Price will not update for Foreign Purchase (LC & TT). Because landed cost are not added on PO
        #     po = self.env['purchase.order'].suspend_security().search([('name', '=', move.origin)], limit=1)
        #     if not po:
        #         continue
        #     if po.region_type in ('foreign') or po.purchase_by in ('lc','tt'):
        #         continue
        #     # End Custom Logic For GBS
        #
        #     product_tot_qty_available = move.product_id.qty_available + tmpl_dict[move.product_id.id]
        #
        #     # if the incoming move is for a purchase order with foreign currency, need to call this to get the same value that the quant will use.
        #     if product_tot_qty_available <= 0:
        #         new_std_price = move.get_price_unit()
        #     else:
        #         # Get the standard price
        #         amount_unit = std_price_update.get((move.company_id.id, move.product_id.id)) or move.product_id.standard_price
        #         new_std_price = ((amount_unit * product_tot_qty_available) + (move.get_price_unit() * move.product_qty)) / (product_tot_qty_available + move.product_qty)
        #
        #     tmpl_dict[move.product_id.id] += move.product_qty
        #     # Write the standard price, as SUPERUSER_ID because a warehouse manager may not have the right to write on products
        #     move.product_id.with_context(force_company=move.company_id.id).sudo().write({'standard_price': new_std_price})
        #     std_price_update[move.company_id.id, move.product_id.id] = new_std_price
