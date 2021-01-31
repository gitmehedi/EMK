# imports of python lib
from datetime import datetime

# imports of odoo
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round


class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"

    @api.multi
    def do_produce(self):
        """Override do_produce to set the value of product_uom_qty"""
        # Nothing to do for lots since values are created using default data (stock.move.lots)
        moves = self.production_id.move_raw_ids
        quantity = self.product_qty
        if float_compare(quantity, 0, precision_rounding=self.product_uom_id.rounding) <= 0:
            raise UserError(_('You should at least produce some quantity'))
        for move in moves.filtered(lambda x: x.product_id.tracking == 'none' and x.state not in ('done', 'cancel')):
            if move.unit_factor:
                rounding = move.product_uom.rounding
                move.quantity_done_store += float_round(quantity * move.unit_factor, precision_rounding=rounding)
                # set To Consume for Raw Materials
                move.product_uom_qty = move.quantity_done_store
        moves = self.production_id.move_finished_ids.filtered(
            lambda x: x.product_id.tracking == 'none' and x.state not in ('done', 'cancel'))
        for move in moves:
            rounding = move.product_uom.rounding
            if move.product_id.id == self.production_id.product_id.id:
                move.quantity_done_store += float_round(quantity, precision_rounding=rounding)
                # set To Consume for Finish Goods
                move.product_uom_qty = move.quantity_done_store
            elif move.unit_factor:
                # byproducts handling
                move.quantity_done_store += float_round(quantity * move.unit_factor, precision_rounding=rounding)
                # set To Consume for Finish Goods
                move.product_uom_qty = move.quantity_done_store
        self.check_finished_move_lots()
        if self.production_id.state == 'confirmed':
            self.production_id.write({
                'state': 'progress',
                'date_start': datetime.now(),
            })

        # check continue production
        done_moves = self.production_id.move_finished_ids.filtered(lambda x: x.state != 'cancel' and x.product_id.id == self.production_id.product_id.id)
        qty_produced = sum(done_moves.mapped('quantity_done'))

        if qty_produced < self.production_id.product_qty:
            # confirmation wizard view
            view = self.env.ref('mrp_extend.view_mrp_production_confirmation')
            wiz = self.env['mrp.production.confirmation'].create({'production_id': self.production_id.id})
            return {
                'name': _('Continue Production?'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mrp.production.confirmation',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        return {'type': 'ir.actions.act_window_close'}
