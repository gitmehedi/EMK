# import of odoo
from odoo import api, fields, models, _
from odoo.tools import frozendict


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def product_price_update_before_done(self):
        for move in self.filtered(lambda move: move.location_id.usage in ('supplier', 'production') and move.product_id.cost_method == 'average'):
            context = dict(self.env.context)
            context.update({'datetime_of_price_history': move.picking_id.date_done or move.production_id.date_planned_start})
            self.env.context = frozendict(context)
            break

        super(StockMove, self).product_price_update_before_done()
