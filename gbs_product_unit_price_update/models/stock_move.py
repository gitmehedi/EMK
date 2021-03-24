from collections import defaultdict

# imports of odoo
from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def product_price_update_before_done(self):

        # Start Custom Logic For GBS : Unit Price will not update for Foreign Purchase (LC & TT). Because landed cost are not added on PO

        for move in self.filtered(lambda move: move.location_id.usage in ('supplier', 'production') and move.product_id.cost_method == 'average'):

            # po = self.env['purchase.order'].suspend_security().search([('name', '=', move.origin)], limit=1)
            lc = self.env['letter.credit'].suspend_security().search([('name', '=', move.origin)], limit=1)
            if lc:
                return
            # if not po:
            #     # It's mean move coming form production. So need to update Finish goods Unit Price
            #     return super(StockMove, self).product_price_update_before_done()
            #
            # if po.region_type in ('foreign') or po.purchase_by in ('lc','tt'):
            #     return

        super(StockMove, self).product_price_update_before_done()

        # End Custom Logic For GBS