# imports of python
from datetime import datetime

# imports of odoo
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round


class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"

    @api.multi
    def do_produce(self):
        # Nothing to do for lots since values are created using default data (stock.move.lots)
        moves = self.production_id.move_raw_ids
        quantity = self.product_qty
        if float_compare(quantity, 0, precision_rounding=self.product_uom_id.rounding) <= 0:
            raise UserError(_('You should at least produce some quantity'))
        for move in moves.filtered(lambda x: x.product_id.tracking == 'none' and x.state not in ('done', 'cancel')):
            if move.unit_factor:
                rounding = move.product_uom.rounding
                # move.quantity_done_store += float_round(quantity * move.unit_factor, precision_rounding=rounding)
                # newly added
                move.quantity_done_store = float_round(quantity * move.unit_factor, precision_rounding=rounding)
                move.product_uom_qty = move.quantity_done_store
                move.standard_qty = move.quantity_done_store

        moves = self.production_id.move_finished_ids.filtered(
            lambda x: x.product_id.tracking == 'none' and x.state not in ('done', 'cancel'))
        for move in moves:
            rounding = move.product_uom.rounding
            if move.product_id.id == self.production_id.product_id.id:
                # move.quantity_done_store += float_round(quantity, precision_rounding=rounding)
                # newly added
                move.quantity_done_store = float_round(quantity, precision_rounding=rounding)
                move.product_uom_qty = move.quantity_done_store
            elif move.unit_factor:
                # byproducts handling
                # move.quantity_done_store += float_round(quantity * move.unit_factor, precision_rounding=rounding)
                # newly added
                move.quantity_done_store = float_round(quantity * move.unit_factor, precision_rounding=rounding)
                move.product_uom_qty = move.quantity_done_store
        self.check_finished_move_lots()
        if self.production_id.state == 'confirmed':
            self.production_id.write({
                'state': 'progress',
                'date_start': datetime.now(),
            })
        return {'type': 'ir.actions.act_window_close'}