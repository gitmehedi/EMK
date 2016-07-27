# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError

class inherited_stock_return_picking(osv.osv_memory):
    _inherit = 'stock.return.picking'


    def _create_returns(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        move_obj = self.pool.get('stock.move')
        pick_obj = self.pool.get('stock.picking')
        uom_obj = self.pool.get('product.uom')
        data_obj = self.pool.get('stock.return.picking.line')
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        data = self.read(cr, uid, ids[0], context=context)
        returned_lines = 0
#         move_data = move_obj.search(cr, uid, [('picking_id', '=', record_id)], context=context)
#         move_record = move_obj.browse(cr, uid, move_data, context=context)


        # Cancel assignment of existing chained assigned moves
        moves_to_unreserve = []
        for move in pick.move_lines:
            to_check_moves = [move.move_dest_id] if move.move_dest_id.id else []
            while to_check_moves:
                current_move = to_check_moves.pop()
                if current_move.state not in ('done', 'cancel') and current_move.reserved_quant_ids:
                    moves_to_unreserve.append(current_move.id)
                split_move_ids = move_obj.search(cr, uid, [('split_from', '=', current_move.id)], context=context)
                if split_move_ids:
                    to_check_moves += move_obj.browse(cr, uid, split_move_ids, context=context)

        if moves_to_unreserve:
            move_obj.do_unreserve(cr, uid, moves_to_unreserve, context=context)
            # break the link between moves in order to be able to fix them later if needed
            move_obj.write(cr, uid, moves_to_unreserve, {'move_orig_ids': False}, context=context)

        # Create new picking for returned products
        pick_type_id = pick.picking_type_id.return_picking_type_id and pick.picking_type_id.return_picking_type_id.id or pick.picking_type_id.id
        new_picking = pick_obj.copy(cr, uid, pick.id, {
            'move_lines': [],
            'picking_type_id': pick_type_id,
            'state': 'draft',
            'origin': pick.name,
            'location_id': pick.location_dest_id.id,
            'location_dest_id': data['location_id'] and data['location_id'][0] or pick.location_id.id,
        }, context=context)

        for data_get in data_obj.browse(cr, uid, data['product_return_moves'], context=context):
            move = data_get.move_id
            if not move:
                raise UserError(_("You have manually created product lines, please delete them to proceed"))
            new_qty = data_get.quantity

            qty_received = data_get.move_id.purchase_line_id.qty_received
            if(qty_received < new_qty):
                raise UserError(_('Return quantity will not be greater than receive quantity.'))
            if new_qty:
                # The return of a return should be linked with the original's destination move if it was not cancelled
                if move.origin_returned_move_id.move_dest_id.id and move.origin_returned_move_id.move_dest_id.state != 'cancel':
                    move_dest_id = move.origin_returned_move_id.move_dest_id.id
                else:
                    move_dest_id = False

                returned_lines += 1
                location_id = data['location_id'] and data['location_id'][0] or move.location_id.id
                move_obj.copy(cr, uid, move.id, {
                    'product_id': data_get.product_id.id,
                    'product_uom_qty': new_qty,
                    'picking_id': new_picking,
                    'state': 'draft',
                    'location_id': move.location_dest_id.id,
                    'location_dest_id': location_id,
                    'picking_type_id': pick_type_id,
                    'warehouse_id': pick.picking_type_id.warehouse_id.id,
                    'origin_returned_move_id': move.id,
                    'procure_method': 'make_to_stock',
                    'move_dest_id': move_dest_id,
                })

        if not returned_lines:
            raise UserError(_("Please specify at least one non-zero quantity."))

        pick_obj.action_confirm(cr, uid, [new_picking], context=context)
        pick_obj.action_assign(cr, uid, [new_picking], context=context)
        return new_picking, pick_type_id

 
