# imports of odoo
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare, float_round


class StockMove(models.Model):
    _inherit = 'stock.move'

    quantity_done_store = fields.Float(digits=dp.get_precision('Product Unit of Measure'))

    standard_qty = fields.Float(string='Standard Qty', readonly=True, digits=dp.get_precision('Product Unit of Measure'))
    check_to_done = fields.Boolean(compute='_compute_check_to_done')

    @api.depends('raw_material_production_id.check_to_done')
    def _compute_check_to_done(self):
        for move in self:
            move.check_to_done = move.raw_material_production_id.check_to_done

    @api.multi
    def _qty_done_set(self):
        """Override _qty_done_set to update the value of product_uom_qty field"""
        for move in self:
            if move.has_tracking == 'none':
                move.quantity_done_store = move.quantity_done
                # for raw materials
                if move.raw_material_production_id and move.quantity_done > 0:
                    move.product_uom_qty = move.quantity_done

    @api.multi
    def unlink(self):
        if any(move.raw_material_production_id for move in self):
            if any(move.bom_line_id for move in self):
                raise UserError(_("Sorry !!!! You cannot remove Raw Material(s) which are coming from BOM"))

            if any(move.state not in ('draft', 'confirmed', 'cancel') for move in self):
                raise UserError(_('You cannot remove Raw Materiel(s) not in confirmed state.'))

            return models.Model.unlink(self)

        return super(StockMove, self).unlink()

    @api.multi
    def move_validate(self):
        # Override move_validate to remove rounding
        ''' Validate moves based on a production order. '''
        moves = self._filter_closed_moves()
        quant_obj = self.env['stock.quant']
        moves_todo = self.env['stock.move']
        moves_to_unreserve = self.env['stock.move']
        # Create extra moves where necessary
        for move in moves:
            # Here, the `quantity_done` was already rounded to the product UOM by the `do_produce` wizard. However,
            # it is possible that the user changed the value before posting the inventory by a value that should be
            # rounded according to the move's UOM. In this specific case, we chose to round up the value, because it
            # is what is expected by the user (if i consumed/produced a little more, the whole UOM unit should be
            # consumed/produced and the moves are split correctly).
            if move.quantity_done <= 0:
                continue
            moves_todo |= move
            moves_todo |= move._create_extra_move()
        # Split moves where necessary and move quants
        for move in moves_todo:
            rounding = move.product_uom.rounding
            if float_compare(move.quantity_done, move.product_uom_qty, precision_rounding=rounding) < 0:
                # Need to do some kind of conversion here
                qty_split = move.product_uom._compute_quantity(move.product_uom_qty - move.quantity_done,
                                                               move.product_id.uom_id)
                new_move = move.split(qty_split)
                # If you were already putting stock.move.lots on the next one in the work order, transfer those to the new move
                move.move_lot_ids.filtered(lambda x: not x.done_wo or x.quantity_done == 0.0).write(
                    {'move_id': new_move})
                self.browse(new_move).quantity_done = 0.0
            main_domain = [('qty', '>', 0)]
            preferred_domain = [('reservation_id', '=', move.id)]
            fallback_domain = [('reservation_id', '=', False)]
            fallback_domain2 = ['&', ('reservation_id', '!=', move.id), ('reservation_id', '!=', False)]
            preferred_domain_list = [preferred_domain] + [fallback_domain] + [fallback_domain2]
            if move.has_tracking == 'none':
                quants = quant_obj.quants_get_preferred_domain(move.product_qty, move, domain=main_domain,
                                                               preferred_domain_list=preferred_domain_list)
                self.env['stock.quant'].quants_move(quants, move, move.location_dest_id,
                                                    owner_id=move.restrict_partner_id.id)
            else:
                for movelot in move.active_move_lot_ids:
                    if float_compare(movelot.quantity_done, 0, precision_rounding=rounding) > 0:
                        if not movelot.lot_id:
                            raise UserError(_('You need to supply a lot/serial number.'))
                        qty = move.product_uom._compute_quantity(movelot.quantity_done, move.product_id.uom_id)
                        quants = quant_obj.quants_get_preferred_domain(qty, move, lot_id=movelot.lot_id.id,
                                                                       domain=main_domain,
                                                                       preferred_domain_list=preferred_domain_list)
                        self.env['stock.quant'].quants_move(quants, move, move.location_dest_id,
                                                            lot_id=movelot.lot_id.id,
                                                            owner_id=move.restrict_partner_id.id)
            moves_to_unreserve |= move
            # Next move in production order
            if move.move_dest_id and move.move_dest_id.state not in ('done', 'cancel'):
                move.move_dest_id.action_assign()
        moves_to_unreserve.quants_unreserve()
        moves_todo.write({'state': 'done', 'date': fields.Datetime.now()})
        return moves_todo
