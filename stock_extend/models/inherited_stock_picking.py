import time
from openerp import api, fields, models
from openerp.tools.float_utils import float_compare, float_round
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp import SUPERUSER_ID, api, models

class InheritedStockPicking(models.Model):
	_inherit = 'stock.picking'


	return_type = fields.Boolean(string='Return Type', default=False)
	stock_issue = fields.Boolean(string='Stock Issue', default=False)
	stock_return = fields.Boolean(string='Stock Return', default=False)
	stock_transfer = fields.Boolean(string='Stock Transfer', default=False)
	picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type', 
						states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
						required=True)
	good_receive_flag = fields.Boolean(string='Good Receive', default=False)
	qc_receive_flag = fields.Boolean(string='QC Receive', default=False)
	qc_pass_flag = fields.Boolean(string='QC Pass', default=False)
	
	'''
	def action_assign(self, cr, uid, ids, context=None):
	    """ Check availability of picking moves.
	    This has the effect of changing the state and reserve quants on available moves, and may
	    also impact the state of the picking as it is computed based on move's states.
	    @return: True
	    """
	    for pick in self.browse(cr, uid, ids, context=context):
	        if pick.state == 'draft':
	            self.action_confirm(cr, uid, [pick.id], context=context)
	        #skip the moves that don't need to be checked
	        move_ids = [x.id for x in pick.move_lines if x.state not in ('draft', 'cancel', 'done')]
	        print '+++++++---move_ids------',move_ids
	        if not move_ids:
	            raise UserError(_('Nothing to check the availability for.'))
	        self.pool.get('stock.move').action_assign(cr, uid, move_ids, context=context)
	    return True
	'''
class InheritedStockMove(models.Model):
	_inherit = 'stock.move'
	
	'''
	def action_assign(self, cr, uid, ids, no_prepare=False, context=None):
	    """ Checks the product type and accordingly writes the state.
	    """
	    context = context or {}
	    quant_obj = self.pool.get("stock.quant")
	    uom_obj = self.pool['product.uom']
	    to_assign_moves = set()
	    main_domain = {}
	    todo_moves = []
	    operations = set()
	    self.do_unreserve(cr, uid, [x.id for x in self.browse(cr, uid, ids, context=context) if x.reserved_quant_ids and x.state in ['confirmed', 'waiting', 'assigned']], context=context)
	    for move in self.browse(cr, uid, ids, context=context):
	        if move.state not in ('confirmed', 'waiting', 'assigned'):
	            continue
	        if move.location_id.usage in ('supplier', 'inventory', 'production'):
	            to_assign_moves.add(move.id)
	            #in case the move is returned, we want to try to find quants before forcing the assignment
	            if not move.origin_returned_move_id:
	                continue
	        if move.product_id.type == 'consu':
	            to_assign_moves.add(move.id)
	            continue
	        else:
	            todo_moves.append(move)
	
	            #we always search for yet unassigned quants
	            main_domain[move.id] = [('reservation_id', '=', False), ('qty', '>', 0)]
	
	            #if the move is preceeded, restrict the choice of quants in the ones moved previously in original move
	            ancestors = self.find_move_ancestors(cr, uid, move, context=context)
	            if move.state == 'waiting' and not ancestors:
	                #if the waiting move hasn't yet any ancestor (PO/MO not confirmed yet), don't find any quant available in stock
	                main_domain[move.id] += [('id', '=', False)]
	            elif ancestors:
	                main_domain[move.id] += [('history_ids', 'in', ancestors)]
	
	            #if the move is returned from another, restrict the choice of quants to the ones that follow the returned move
	            if move.origin_returned_move_id:
	                main_domain[move.id] += [('history_ids', 'in', move.origin_returned_move_id.id)]
	            for link in move.linked_move_operation_ids:
	                operations.add(link.operation_id)
	    # Check all ops and sort them: we want to process first the packages, then operations with lot then the rest
	    operations = list(operations)
	    operations.sort(key=lambda x: ((x.package_id and not x.product_id) and -4 or 0) + (x.package_id and -2 or 0) + (x.pack_lot_ids and -1 or 0))
	    for ops in operations:
	        #first try to find quants based on specific domains given by linked operations for the case where we want to rereserve according to existing pack operations
	        if not (ops.product_id and ops.pack_lot_ids):
	            for record in ops.linked_move_operation_ids:
	                move = record.move_id
	                if move.id in main_domain:
	                    qty = record.qty
	                    domain = main_domain[move.id]
	                    if qty:
	                        quants = quant_obj.quants_get_preferred_domain(cr, uid, qty, move, ops=ops, domain=domain, preferred_domain_list=[], context=context)
	                        quant_obj.quants_reserve(cr, uid, quants, move, record, context=context)
	        else:
	            lot_qty = {}
	            rounding = ops.product_id.uom_id.rounding
	            for pack_lot in ops.pack_lot_ids:
	                lot_qty[pack_lot.lot_id.id] = uom_obj._compute_qty(cr, uid, ops.product_uom_id.id, pack_lot.qty, ops.product_id.uom_id.id)
	            for record in ops.linked_move_operation_ids:
	                move_qty = record.qty
	                move = record.move_id
	                domain = main_domain[move.id]
	                for lot in lot_qty:
	                    if float_compare(lot_qty[lot], 0, precision_rounding=rounding) > 0 and float_compare(move_qty, 0, precision_rounding=rounding) > 0:
	                        qty = min(lot_qty[lot], move_qty)
	                        quants = quant_obj.quants_get_preferred_domain(cr, uid, qty, move, ops=ops, lot_id=lot, domain=domain, preferred_domain_list=[], context=context)
	                        quant_obj.quants_reserve(cr, uid, quants, move, record, context=context)
	                        lot_qty[lot] -= qty
	                        move_qty -= qty
	
	    for move in todo_moves:
	    	print '---------move---------',move
	        #then if the move isn't totally assigned, try to find quants without any specific domain
	        if move.state != 'assigned':
	            qty_already_assigned = move.reserved_availability
	            qty = move.product_qty - qty_already_assigned
	            quants = quant_obj.quants_get_preferred_domain(cr, uid, qty, move, domain=main_domain[move.id], preferred_domain_list=[], context=context)
	            print '---------quants---------',quants
	            quant_obj.quants_reserve(cr, uid, quants, move, context=context)
	
	    #force assignation of consumable products and incoming from supplier/inventory/production
	    # Do not take force_assign as it would create pack operations
	    if to_assign_moves:
	        self.write(cr, uid, list(to_assign_moves), {'state': 'assigned'}, context=context)
	    if not no_prepare:
	        self.check_recompute_pack_op(cr, uid, ids, context=context)
	 '''       
	def action_done(self, cr, uid, ids, context=None):
	    """ Process completely the moves given as ids and if all moves are done, it will finish the picking.
	    """
	    context = context or {}
	    picking_obj = self.pool.get("stock.picking")
	    quant_obj = self.pool.get("stock.quant")
	    uom_obj = self.pool.get("product.uom")
	    todo = [move.id for move in self.browse(cr, uid, ids, context=context) if move.state == "draft"]
	    if todo:
	        ids = self.action_confirm(cr, uid, todo, context=context)
	    pickings = set()
	    procurement_ids = set()
	    #Search operations that are linked to the moves
	    operations = set()
	    move_qty = {}
	    for move in self.browse(cr, uid, ids, context=context):
	        move_qty[move.id] = move.product_qty
	        for link in move.linked_move_operation_ids:
	            operations.add(link.operation_id)
	
	    #Sort operations according to entire packages first, then package + lot, package only, lot only
	    operations = list(operations)
	    operations.sort(key=lambda x: ((x.package_id and not x.product_id) and -4 or 0) + (x.package_id and -2 or 0) + (x.pack_lot_ids and -1 or 0))
	
	    for ops in operations:
	        if ops.picking_id:
	            pickings.add(ops.picking_id.id)
	        entire_pack=False
	        if ops.product_id:
	            #If a product is given, the result is always put immediately in the result package (if it is False, they are without package)
	            quant_dest_package_id  = ops.result_package_id.id
	        else:
	            # When a pack is moved entirely, the quants should not be written anything for the destination package
	            quant_dest_package_id = False
	            entire_pack=True
	        lot_qty = {}
	        tot_qty = 0.0
	        for pack_lot in ops.pack_lot_ids:
	            qty = uom_obj._compute_qty(cr, uid, ops.product_uom_id.id, pack_lot.qty, ops.product_id.uom_id.id)
	            lot_qty[pack_lot.lot_id.id] = qty
	            tot_qty += pack_lot.qty
	        if ops.pack_lot_ids and ops.product_id and float_compare(tot_qty, ops.product_qty, precision_rounding=ops.product_uom_id.rounding) != 0.0:
	            raise UserError(_('You have a difference between the quantity on the operation and the quantities specified for the lots. '))
	
	        quants_taken = []
	        false_quants = []
	        lot_move_qty = {}
	        #Group links by move first
	        move_qty_ops = {}
	        for record in ops.linked_move_operation_ids:
	            move = record.move_id
	            if not move_qty_ops.get(move):
	                move_qty_ops[move] = record.qty
	            else:
	                move_qty_ops[move] += record.qty
	        #Process every move only once for every pack operation
	        for move in move_qty_ops:
	            main_domain = [('qty', '>', 0)]
	            self.check_tracking(cr, uid, move, ops, context=context)
	            preferred_domain = [('reservation_id', '=', move.id)]
	            fallback_domain = [('reservation_id', '=', False)]
	            fallback_domain2 = ['&', ('reservation_id', '!=', move.id), ('reservation_id', '!=', False)]
	            if not ops.pack_lot_ids:
	                preferred_domain_list = [preferred_domain] + [fallback_domain] + [fallback_domain2]
	                quants = quant_obj.quants_get_preferred_domain(cr, uid, move_qty_ops[move], move, ops=ops, domain=main_domain,
	                                                    preferred_domain_list=preferred_domain_list, context=context)
	                quant_obj.quants_move(cr, uid, quants, move, ops.location_dest_id, location_from=ops.location_id,
	                                      lot_id=False, owner_id=ops.owner_id.id, src_package_id=ops.package_id.id,
	                                      dest_package_id=quant_dest_package_id, entire_pack=entire_pack, context=context)
	            else:
	                # Check what you can do with reserved quants already
	                qty_on_link = move_qty_ops[move]
	                rounding = ops.product_id.uom_id.rounding
	                for reserved_quant in move.reserved_quant_ids:
	                    if (reserved_quant.owner_id.id != ops.owner_id.id) or (reserved_quant.location_id.id != ops.location_id.id) or \
	                            (reserved_quant.package_id.id != ops.package_id.id):
	                        continue
	                    if not reserved_quant.lot_id:
	                        false_quants += [reserved_quant]
	                    elif float_compare(lot_qty.get(reserved_quant.lot_id.id, 0), 0, precision_rounding=rounding) > 0:
	                        if float_compare(lot_qty[reserved_quant.lot_id.id], reserved_quant.qty, precision_rounding=rounding) >= 0:
	                            lot_qty[reserved_quant.lot_id.id] -= reserved_quant.qty
	                            quants_taken += [(reserved_quant, reserved_quant.qty)]
	                            qty_on_link -= reserved_quant.qty
	                        else:
	                            quants_taken += [(reserved_quant, lot_qty[reserved_quant.lot_id.id])]
	                            lot_qty[reserved_quant.lot_id.id] = 0
	                            qty_on_link -= lot_qty[reserved_quant.lot_id.id]
	                lot_move_qty[move.id] = qty_on_link
	
	            if not move_qty.get(move.id):
	                raise UserError(_("The roundings of your Unit of Measures %s on the move vs. %s on the product don't allow to do these operations or you are not transferring the picking at once. ") % (move.product_uom.name, move.product_id.uom_id.name))
	            move_qty[move.id] -= move_qty_ops[move]
	
	        #Handle lots separately
	        if ops.pack_lot_ids:
	            self._move_quants_by_lot(cr, uid, ops, lot_qty, quants_taken, false_quants, lot_move_qty, quant_dest_package_id, context=context)
	
	        # Handle pack in pack
	        if not ops.product_id and ops.package_id and ops.result_package_id.id != ops.package_id.parent_id.id:
	            self.pool.get('stock.quant.package').write(cr, SUPERUSER_ID, [ops.package_id.id], {'parent_id': ops.result_package_id.id}, context=context)
	    #Check for remaining qtys and unreserve/check move_dest_id in
	    move_dest_ids = set()
	    for move in self.browse(cr, uid, ids, context=context):
	        move_qty_cmp = float_compare(move_qty[move.id], 0, precision_rounding=move.product_id.uom_id.rounding)
	        if move_qty_cmp > 0:  # (=In case no pack operations in picking)
	            main_domain = [('qty', '>', 0)]
	            preferred_domain = [('reservation_id', '=', move.id)]
	            fallback_domain = [('reservation_id', '=', False)]
	            fallback_domain2 = ['&', ('reservation_id', '!=', move.id), ('reservation_id', '!=', False)]
	            preferred_domain_list = [preferred_domain] + [fallback_domain] + [fallback_domain2]
	            self.check_tracking(cr, uid, move, False, context=context)
	            qty = move_qty[move.id]
	            quants = quant_obj.quants_get_preferred_domain(cr, uid, qty, move, domain=main_domain, preferred_domain_list=preferred_domain_list, context=context)
	            quant_obj.quants_move(cr, uid, quants, move, move.location_dest_id, lot_id=move.restrict_lot_id.id, owner_id=move.restrict_partner_id.id, context=context)
	
	        # If the move has a destination, add it to the list to reserve
	        if move.move_dest_id and move.move_dest_id.state in ('waiting', 'confirmed'):
	            move_dest_ids.add(move.move_dest_id.id)
	
	        if move.procurement_id:
	            procurement_ids.add(move.procurement_id.id)
	
	        #unreserve the quants and make them available for other operations/moves
	        quant_obj.quants_unreserve(cr, uid, move, context=context)
	    # Check the packages have been placed in the correct locations
	    self._check_package_from_moves(cr, uid, ids, context=context)
	    #set the move as done
	    self.write(cr, uid, ids, {'state': 'done', 'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}, context=context)
	    self.pool.get('procurement.order').check(cr, uid, list(procurement_ids), context=context)
	    #assign destination moves
	    if move_dest_ids:
	        self.action_assign(cr, uid, list(move_dest_ids), context=context)
	    #check picking state to set the date_done is needed
	    done_picking = []
	    for picking in picking_obj.browse(cr, uid, list(pickings), context=context):
	        if picking.state == 'done' and not picking.date_done:
	            done_picking.append(picking.id)
	    picking_obj.write(cr, uid, picking.id,{'qc_receive_flag':True}, context=context)
	    if done_picking:
	        picking_obj.write(cr, uid, done_picking, {'date_done': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}, context=context)
	    return True
	'''       	
class InheritStockQuant(models.Model):
	_inherit = "stock.quant"
    
	def quants_reserve(self, cr, uid, quants, move, link=False, context=None):
	    toreserve = []
	    reserved_availability = move.reserved_availability
	    #split quants if needed
	    for quant, qty in quants:
	        if qty <= 0.0 or (quant and quant.qty <= 0.0):
	            raise UserError(_('You can not reserve a negative quantity or a negative quant.'))
	        if not quant:
	            continue
	        self._quant_split(cr, uid, quant, qty, context=context)
	        toreserve.append(quant.id)
	        reserved_availability += quant.qty
	    	print "--------quant --------",quant
	    	print "--------qty --------",qty
	    	print "--------quant.qty --------",quant.qty
	    	print "--------reserved_availability.qty --------",reserved_availability
	    print "--------product_id 2222222-----",move.product_id
	    print "--------move 2222222-----",move
	    print "--------move.reserved_availability  2222222-----",move.reserved_availability    
	    reserve_obj = self.pool.get('reservation.quant').search(cr, uid, [('product_id','=',move.product_id.id)])
	    print "-++++++++++=-----reserve_obj----------",reserve_obj
	    
	    if reserve_obj:
	    	obj_reser = self.pool['reservation.quant'].browse(cr, uid, reserve_obj)
	    	print "-++++++++++=-----obj_reser----------",obj_reser
	    	print "-++++++++++=-----reserve_quantity----------",obj_reser.reserve_quantity
	    	reserved_availability += obj_reser.reserve_quantity
	    #reserve quants
	    if toreserve:
	        self.write(cr, SUPERUSER_ID, toreserve, {'reservation_id': move.id}, context=context)
	    #check if move'state needs to be set as 'assigned'
	    print "--------reserved_availability 11111111-----",reserved_availability
	    print "--------product_id 11111111-----",move.product_id
	    print "--------product_qty 11111111-----",move.product_qty
	    rounding = move.product_id.uom_id.rounding
	    if float_compare(reserved_availability, move.product_qty, precision_rounding=rounding) == 0 and move.state in ('confirmed', 'waiting')  :
	        self.pool.get('stock.move').write(cr, uid, [move.id], {'state': 'assigned'}, context=context)
	    elif float_compare(reserved_availability, 0, precision_rounding=rounding) > 0 and not move.partially_available:
	    	print "-------rounding---------",rounding
	        self.pool.get('stock.move').write(cr, uid, [move.id], {'partially_available': True}, context=context)
	'''        
class InheritPurchaseOrder(models.Model):
	_inherit = "purchase.order"
	
	@api.model
	def _prepare_picking(self):
	    if not self.group_id:
	        self.group_id = self.group_id.create({
	            'name': self.name,
	            'partner_id': self.partner_id.id
	        })
	    return {
	        'picking_type_id': self.picking_type_id.id,
	        'partner_id': self.partner_id.id,
	        'date': self.date_order,
	        'origin': self.name,
	        'location_dest_id': self._get_destination_location(),
	        'location_id': self.partner_id.property_stock_supplier.id,
	        'good_receive_flag':True
	    }