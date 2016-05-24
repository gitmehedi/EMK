from datetime import date, datetime
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
	def create(self, cr, user, vals, context=None):
	    context = context or {}
	    print "_____pick______",self,"___vals_--",vals
	    if ('name' not in vals) or (vals.get('name') in ('/', False)):
	        ptype_id = vals.get('picking_type_id', context.get('default_picking_type_id', False))
	        sequence_id = self.pool.get('stock.picking.type').browse(cr, user, ptype_id, context=context).sequence_id.id
	        vals['name'] = self.pool.get('ir.sequence').next_by_id(cr, user, sequence_id, context=context)
	    # As the on_change in one2many list is WIP, we will overwrite the locations on the stock moves here
	    # As it is a create the format will be a list of (0, 0, dict)
	    if vals.get('move_lines') and vals.get('location_id') and vals.get('location_dest_id'):
	        for move in vals['move_lines']:
	            if len(move) == 3:
	                move[2]['location_id'] = vals['location_id']
	                move[2]['location_dest_id'] = vals['location_dest_id']
	    return super(InheritedStockPicking, self).create(cr, user, vals, context)
	'''
	   
class InheritedStockMove(models.Model):
    _inherit = 'stock.move'
	

    def check_recompute_pack_op(self, cr, uid, ids, context=None):
        pickings = list(set([x.picking_id for x in self.browse(cr, uid, ids, context=context) if x.picking_id]))
        pickings_partial = []
        pickings_write = []
        pick_obj = self.pool['stock.picking']
        for pick in pickings:
            if pick.state in ('waiting', 'confirmed'): #In case of 'all at once' delivery method it should not prepare pack operations
                continue
            # Check if someone was treating the picking already
            if not any([x.qty_done > 0 for x in pick.pack_operation_ids]):
                pickings_partial.append(pick.id)
            else:
                pickings_write.append(pick.id)
    # 		print '+++++++++++++++--___pick.id___-----',pick.id
    # 		print '+++++++++++++++--___pick.state___-----',pick.state
    # 		print '+++++++++++++++--___good_receive_flag___-----',pick.good_receive_flag
    # 		print '+++++++++++++++--___pick.qc_receive_flag___-----',pick.qc_receive_flag
    # 		print '+++++++++++++++--___pick.qc_pass_flag___-----',pick.qc_pass_flag
    # 		if (pick.good_receive_flag == False) and (pick.qc_receive_flag == False) and (pick.state == "assigned" or pick.state == "partially_available"):
    # 			pick_obj.write(cr, uid, pick.id, {'qc_receive_flag': True}, context=context)
    # 		
    # 		elif (pick.good_receive_flag == False) and (pick.qc_receive_flag == True) and (pick.qc_pass_flag == False) and (pick.qc_pass_flag == False)  and (pick.state == "assigned" or pick.state == "partially_available"):
    # 				pick_obj.write(cr, uid, pick.id, {'qc_pass_flag': True}, context=context)
    	
    	if pickings_partial:
    	    pick_obj.do_prepare_partial(cr, uid, pickings_partial, context=context)
    	if pickings_write:
    	    pick_obj.write(cr, uid, pickings_write, {'recompute_pack_op': True}, context=context)
    
        return True
    
    @api.cr_uid_ids_context
    def _picking_assign(self, cr, uid, move_ids, context=None):
        """Try to assign the moves to an existing picking
        that has not been reserved yet and has the same
        procurement group, locations and picking type  (moves should already have them identical)
         Otherwise, create a new picking to assign them to.
        """
        move = self.browse(cr, uid, move_ids, context=context)[0]
        pick_obj = self.pool.get("stock.picking")
        picks = pick_obj.search(cr, uid, [
                ('group_id', '=', move.group_id.id),
                ('location_id', '=', move.location_id.id),
                ('location_dest_id', '=', move.location_dest_id.id),
                ('picking_type_id', '=', move.picking_type_id.id),
                ('printed', '=', False),
                ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned'])], limit=1, context=context)
        if picks:
            pick = picks[0]
        else:
            values = self._prepare_picking_assign(cr, uid, move, context=context)
            values.update({'qc_receive_flag': True,'qc_pass_flag': False})
            picking_exist = pick_obj.search(cr, uid,[('origin', '=', values['origin']), ('qc_receive_flag', '=', True)], limit=1, context=context)
            if(picking_exist):
            	values.update({'qc_receive_flag': False,'qc_pass_flag': True})

            pick = pick_obj.create(cr, uid, values, context=context)

        return self.write(cr, uid, move_ids, {'picking_id': pick}, context=context)
    
      
class InheritPurchaseOrder(models.Model):
	_inherit = "purchase.order"
	
	@api.model
	def _prepare_picking(self):
		print '########____prepare_picking_____######'
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
		
	
