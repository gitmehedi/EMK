from openerp import api, exceptions, fields, models
from datetime import date
import time
from openerp.exceptions import Warning
from openerp.tools.translate import _

class StockReportWizard(models.TransientModel):
	_name = 'stock.report.wizard'

	start_date = fields.Date('Start Date', default=fields.Date.today())
	end_date = fields.Date('End Date', default=fields.Date.today())
	stock_type = fields.Selection([('1', "Issue"), ('2', "Return"), ('3', "Transfer")],default="0")
	source_loc = fields.Many2one('stock.location', 'Source Location')
	desti_loc = fields.Many2one('stock.location', 'Destination Location')
	_sql_constraints = [
        ('_check_date_comparison', "CHECK ( (start_date <= end_date))", "The Start date must be lower than End date.")
    ]
	
	"""
	def stock_issue_report(self, cr, uid, ids, context=None):
		datas = {}
		if context is None:
		    context = {}
		data = self.read(cr, uid, ids,['start_date', 'end_date'], context=context)
		start_date = data[0]['start_date'] 
		end_date = data[0]['end_date']
		obj_picking = self.pool.get('stock.picking')
		picking_ids = obj_picking.search(cr, uid, [('create_date','>=',start_date),('create_date','<=',end_date),('stock_issue','=',True)])
		print 'picking_ids ', picking_ids
		obj_move = self.pool.get('stock.move')
		ids = obj_move.search(cr, uid, [('picking_id','in',picking_ids)])
		
		print 'ids ', ids

		datas = {
		         'ids': ids,
		         'model': 'stock.report.wizard',
		         'form': data
		        }
		
		return {
			'type': 'ir.actions.report.xml',
			'report_name': 'stock_extend.report_stock_issue_qweb',
			'datas': datas,
			'name': 'stock-report-' + start_date + ' To ' + end_date,
			 }
	
	
	def stock_issue_report(self, cr, uid, ids, data, context=None):
	    if context is None:
	        context = {}
	    dict = {}
	    product_list = []
	    bookz = self.browse(cr, uid, ids, context=context)
	    picking_ids = self.pool.get('stock.picking').search(cr, uid, [('create_date', '>=', bookz.start_date), ('create_date', '<=', bookz.end_date), ('stock_issue', '=', True)])
	    mov_obj = self.pool.get('stock.move')
	    ids2 = mov_obj.search(cr, uid, [('picking_id', 'in', picking_ids)])

	    for line in ids2:
			obj_move = mov_obj.browse(cr, uid, line, context=context);
			dict ={'id':obj_move.id,'product_name':obj_move.product_id.name, 'product_qty':obj_move.product_qty,'product_uom':obj_move.product_uom.name, 'source_loc':obj_move.location_id.name,'dest_loc':obj_move.location_dest_id.name}
			product_list.append(dict)
	    data['ids'] = product_list 
	    data['form'] = self.read(cr, uid, ids, ['start_date', 'end_date'], context=context)[0]
	    if not data['form']['start_date']:  # GTK client problem onchange does not consider in save record
	        data['form'].update({'start_date': False})
	
	    if data['form']['end_date'] is False:
	        data['form'].pop('end_date')
	    return self.pool['report'].get_action(cr, uid, [], 'stock_extend.report_stock_issue_qweb', data=data, context=context)
	"""
	
	@api.multi	
	def stock_report(self,data):
		picking_id = []
		dict = {}
		product_list = []
		source_location_name = ""
		desti_location_name = ""
		obj_picking = self.env['stock.picking']
		if(self.stock_type=='1'):
			stock_flag = 'stock_issue'
		elif(self.stock_type=='2'):
			stock_flag = 'stock_return'
		elif(self.stock_type=="3"):
			stock_flag = 'stock_transfer'
		picking_ids = obj_picking.search([('date_done','>=',self.start_date),('date_done','<=',self.end_date),(stock_flag,'=',True)])
		
		obj_move = self.env['stock.move']
		for pick_id in picking_ids:
			picking_id.append(pick_id.id)
		
		if(self.source_loc and self.desti_loc):
			source_location_name = self.source_loc.location_id.name+ "/"+ self.source_loc.name
			desti_location_name = self.desti_loc.location_id.name+ "/"+ self.desti_loc.name
			ids = obj_move.search([['picking_id','in',picking_id],['location_id','=',self.source_loc.id],['location_dest_id','=',self.desti_loc.id]])
		elif(self.source_loc and not self.desti_loc):
			source_location_name = self.source_loc.location_id.name+ "/"+ self.source_loc.name
			ids = obj_move.search([['picking_id','in',picking_id],['location_id','=',self.source_loc.id]])
		elif(not self.source_loc and self.desti_loc):
			desti_location_name = self.desti_loc.location_id.name+ "/"+ self.desti_loc.name
			ids = obj_move.search([['picking_id','in',picking_id],['location_dest_id','=',self.desti_loc.id]])
		else:
			ids = obj_move.search([['picking_id','in',picking_id]])
		
		for move_line in ids:
			dict ={'id':move_line.id,'product_name':move_line.product_id.name, 'product_qty':move_line.product_qty,'product_uom':move_line.product_uom.name, 'source_loc':move_line.location_id.name,'dest_loc':move_line.location_dest_id.name}
			product_list.append(dict)
		data['other'] ={'source_location':source_location_name,'desti_location':desti_location_name} 
		data['ids'] = product_list 
		data['form'] = self.read([], ['start_date', 'end_date','stock_type'])[0]
		return self.env['report'].get_action(self, 'stock_extend.report_stock_issue_qweb', data=data)
		