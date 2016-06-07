from datetime import date, datetime
import time
from openerp import api, fields, models
from openerp.tools.float_utils import float_compare, float_round
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp import SUPERUSER_ID, api, models
from openerp.exceptions import UserError

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
	
	min_date = fields.Date('Scheduled Date',default=fields.Date.today(), required=True, readonly=True, states={'draft': [('readonly', False)]})
	
	_sql_constraints = [
        ('_check_date_comparison_pick', "CHECK (date <= min_date)", "The Creation date can not be greater than Scheduled Date.")
    ] 
	
		   
class InheritedStockMove(models.Model):
    _inherit = 'stock.move'
	

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
            values.update({'qc_receive_flag': True, 'qc_pass_flag': False})
            picking_exist = pick_obj.search(cr, uid, [('origin', '=', values['origin']), ('qc_receive_flag', '=', True)], limit=1, context=context)
            if(picking_exist):
            	values.update({'qc_receive_flag': False, 'qc_pass_flag': True})

            pick = pick_obj.create(cr, uid, values, context=context)

        return self.write(cr, uid, move_ids, {'picking_id': pick}, context=context)
    
      
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
		

	  
class InheritStockQuant(models.Model):
	_inherit = "stock.quant"	
	
	def quants_reserve(self, cr, uid, quants, move, link=False, context=None):
	    '''This function reserves quants for the given move (and optionally given link). If the total of quantity reserved is enough, the move's state
	    is also set to 'assigned'
	
	    :param quants: list of tuple(quant browse record or None, qty to reserve). If None is given as first tuple element, the item will be ignored. Negative quants should not be received as argument
	    :param move: browse record
	    :param link: browse record (stock.move.operation.link)
	    '''
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
	    #reserve quants
	    if toreserve:
	        self.write(cr, SUPERUSER_ID, toreserve, {'reservation_id': move.id}, context=context)
	    #check if move'state needs to be set as 'assigned'
	    rounding = move.product_id.uom_id.rounding
	    if float_compare(reserved_availability, move.product_qty, precision_rounding=rounding) == 0 and move.state in ('confirmed', 'waiting')  :
	        self.pool.get('stock.move').write(cr, uid, [move.id], {'state': 'assigned'}, context=context)
	    elif float_compare(reserved_availability, 0, precision_rounding=rounding) > 0 and not move.partially_available:
	        self.pool.get('stock.move').write(cr, uid, [move.id], {'partially_available': True}, context=context)

	
	def _quants_get_order(self, cr, uid, quantity, move, ops=False, domain=[], orderby='in_date', context=None):
		''' Implementation of removal strategies
		    If it can not reserve, it will return a tuple (None, qty)
		'''
		if context is None:
		    context = {}
		product = move.product_id
		res = []
		offset = 0
		resv_qty = 0
		total_qty = 0
		availabile_qty = 0
		sub_quantity = 0
		resv_quant_obj = self.pool.get("reservation.quant")
		resv_exist = resv_quant_obj.search(cr, uid, [('product_id', '=', move.product_id.id), ('location', '=', move.location_id.id)], context=context)
		for resv in resv_exist:
			resv_id = resv_quant_obj.browse(cr, uid, resv, context=context)
			resv_qty += resv_id.reserve_quantity
		
		s_quants = self.search(cr, uid, domain, order=orderby, limit=10, offset=offset, context=context)
		for s_quant in self.browse(cr, uid, s_quants, context=context):
			total_qty += s_quant.qty
		
		for dd in domain:
			if dd[0]=='reservation_id':
				if dd[2] != False:
					resv_qty = 0.0
			
		
		availabile_qty = total_qty - resv_qty
		while float_compare(quantity, 0, precision_rounding=product.uom_id.rounding) > 0:
		    quants = self.search(cr, uid, domain, order=orderby, limit=10, offset=offset, context=context)
		    if not quants:
		        res.append((None, quantity))
		        break
		    if availabile_qty <= 0.0:
		    	quantity = quantity-availabile_qty
		    	res.append((None, quantity))
		        break
		    if availabile_qty < quantity:
		    	sub_quantity = quantity-availabile_qty
		        quantity = availabile_qty
		        for quant in self.browse(cr, uid, quants, context=context):
			        rounding = product.uom_id.rounding
			        if float_compare(quantity, abs(quant.qty), precision_rounding=rounding) >= 0:
			            res += [(quant, abs(quant.qty))]
			            quantity -= abs(quant.qty)
			        elif float_compare(quantity, 0.0, precision_rounding=rounding) != 0:
			            res += [(quant, quantity)]
			            quantity = 0
			            break
			           
				
				
				
		    elif availabile_qty >= quantity:
		    	for quant in self.browse(cr, uid, quants, context=context):
			        rounding = product.uom_id.rounding
			        if float_compare(quantity, abs(quant.qty), precision_rounding=rounding) >= 0:
			            res += [(quant, abs(quant.qty))]
			            quantity -= abs(quant.qty)
			        elif float_compare(quantity, 0.0, precision_rounding=rounding) != 0:
			            res += [(quant, quantity)]
			            quantity = 0
			            break
			
		    	
		    offset += 10
		    if sub_quantity > 0.0:
		    	res.append((None, sub_quantity))
		    	break

		return res
	