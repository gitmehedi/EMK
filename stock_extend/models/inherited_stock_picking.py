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
		
	
