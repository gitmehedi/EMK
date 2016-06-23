from openerp import api, exceptions, fields, models
from datetime import date
import datetime
import time
from openerp.exceptions import Warning
from openerp.tools.translate import _

class GatePassReportWizard(models.TransientModel):
	_name = 'gatepass.report.wizard'

	start_date = fields.Date('Start Date', default=fields.Date.today())
	end_date = fields.Date('End Date', default=fields.Date.today())
	gate_pass_type = fields.Selection([('1', "Gate Pass In"), ('2', "Gate Pass Out")],default="0")
	source_loc = fields.Many2one('stock.location', 'Store Location', domain=[('usage', '=', 'internal')])
	desti_loc = fields.Many2one('stock.location', 'Destination Location')
	_sql_constraints = [
        ('_check_date_comparison', "CHECK ( (start_date <= end_date))", "The Start date must be lower than End date.")
    ]
	
	@api.one
	@api.constrains('start_date', 'end_date')
	def _check_date_validation(self):
		if self.start_date > self.end_date:
			raise exceptions.ValidationError("The start date must be anterior to the end date.")
		
	@api.multi	
	def action_gate_pass_report(self,data):
		gate_pass_id = []
		dict = {}
		product_list = []
		source_location_name = ""
		desti_location_name = ""
		
		if(self.gate_pass_type=='1'):
			obj_gate_pass = self.env['stock.gatepass.in']
			if(self.source_loc and self.desti_loc):
				if self.source_loc.location_id:
					source_location_name = self.source_loc.location_id.name+ "/"+ self.source_loc.name
				else:
					source_location_name = self.source_loc.name
				if self.desti_loc.location_id:
					desti_location_name = self.desti_loc.location_id.name+ "/"+ self.desti_loc.name
				else:
					desti_location_name = self.desti_loc.name
				gate_pass_ids = obj_gate_pass.search([['date','>=',self.start_date],['date','<=',self.end_date],['store_location','=',self.source_loc.id],['source_location','=',self.desti_loc.id]])
			elif(self.source_loc and not self.desti_loc):
				if self.source_loc.location_id:
					source_location_name = self.source_loc.location_id.name+ "/"+ self.source_loc.name
				else:
					source_location_name = self.source_loc.name
				gate_pass_ids = obj_gate_pass.search([['date','>=',self.start_date],['date','<=',self.end_date],['store_location','=',self.source_loc.id]])
			elif(not self.source_loc and self.desti_loc):
				if self.desti_loc.location_id:
					desti_location_name = self.desti_loc.location_id.name+ "/"+ self.desti_loc.name
				else:
					desti_location_name = self.desti_loc.name
				gate_pass_ids = obj_gate_pass.search([['date','>=',self.start_date],['date','<=',self.end_date],['source_location','=',self.desti_loc.id]])
			else:
				gate_pass_ids = obj_gate_pass.search([('date','>=',self.start_date),('date','<=',self.end_date)])
			
		elif(self.gate_pass_type=='2'):
			obj_gate_pass = self.env['stock.gatepass.out']
			if(self.source_loc and self.desti_loc):
				if self.source_loc.location_id:
					source_location_name = self.source_loc.location_id.name+ "/"+ self.source_loc.name
				else:
					source_location_name = self.source_loc.name
				if self.desti_loc.location_id:
					desti_location_name = self.desti_loc.location_id.name+ "/"+ self.desti_loc.name
				else:
					desti_location_name = self.desti_loc.name
				gate_pass_ids = obj_gate_pass.search([['date','>=',self.start_date],['date','<=',self.end_date],['store_location','=',self.source_loc.id],['destination_location','=',self.desti_loc.id]])
			elif(self.source_loc and not self.desti_loc):
				if self.source_loc.location_id:
					source_location_name = self.source_loc.location_id.name+ "/"+ self.source_loc.name
				else:
					source_location_name = self.source_loc.name
				gate_pass_ids = obj_gate_pass.search([['date','>=',self.start_date],['date','<=',self.end_date],['store_location','=',self.source_loc.id]])
			elif(not self.source_loc and self.desti_loc):
				if self.desti_loc.location_id:
					desti_location_name = self.desti_loc.location_id.name+ "/"+ self.desti_loc.name
				else:
					desti_location_name = self.desti_loc.name
				gate_pass_ids = obj_gate_pass.search([['date','>=',self.start_date],['date','<=',self.end_date],['destination_location','=',self.desti_loc.id]])
			else:
				gate_pass_ids = obj_gate_pass.search([('date','>=',self.start_date),('date','<=',self.end_date)])
			
		
		
		for gate_id in gate_pass_ids:
			gate_pass_id.append(gate_id.id)
		
		if(self.gate_pass_type=='1'):	
			ids = self.env['stock.gatepass.in.line'].search([['stock_gatepass_in_id','in',gate_pass_id]])
			for gate_pass_line in ids:
				if gate_pass_line.stock_gatepass_in_id.store_location.location_id:
					source_location_name = gate_pass_line.stock_gatepass_in_id.store_location.location_id.name+ "/"+ gate_pass_line.stock_gatepass_in_id.store_location.name
				else:
					source_location_name = gate_pass_line.stock_gatepass_in_id.store_location.name
				if gate_pass_line.stock_gatepass_in_id.source_location.location_id:
					desti_location_name = gate_pass_line.stock_gatepass_in_id.source_location.location_id.name+ "/"+ gate_pass_line.stock_gatepass_in_id.source_location.name
				else:
					desti_location_name = gate_pass_line.stock_gatepass_in_id.source_location.name
				dis_date=datetime.datetime.strptime(gate_pass_line.stock_gatepass_in_id.date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y')
				dict ={'id':gate_pass_line.id,
					'date':gate_pass_line.stock_gatepass_in_id.date,
					'sl_no':gate_pass_line.stock_gatepass_in_id.gete_pass_no,
					'store_loc':source_location_name,
					'dest_loc':desti_location_name,
					'product_name':gate_pass_line.description,
					'product_qty':gate_pass_line.product_qty,
					'product_uom':gate_pass_line.product_qom.name}
				product_list.append(dict)
		elif(self.gate_pass_type=='2'):
			ids = self.env['stock.gatepass.out.line'].search([['stock_gatepass_out_id','in',gate_pass_id]])
			for gate_pass_line in ids:
				if gate_pass_line.stock_gatepass_out_id.store_location.location_id:
					source_location_name = gate_pass_line.stock_gatepass_out_id.store_location.location_id.name+ "/"+ gate_pass_line.stock_gatepass_out_id.store_location.name
				else:
					source_location_name = gate_pass_line.stock_gatepass_out_id.store_location.name
				if gate_pass_line.stock_gatepass_out_id.destination_location.location_id:
					desti_location_name = gate_pass_line.stock_gatepass_out_id.destination_location.location_id.name+ "/"+ gate_pass_line.stock_gatepass_out_id.destination_location.name
				else:
					desti_location_name = gate_pass_line.stock_gatepass_out_id.destination_location.name
				dis_date=datetime.datetime.strptime(gate_pass_line.stock_gatepass_out_id.date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y')
				
				dict ={'id':gate_pass_line.id,
					'date':gate_pass_line.stock_gatepass_out_id.date,
					'sl_no':gate_pass_line.stock_gatepass_out_id.gete_pass_no,
					'store_loc':source_location_name,
					'dest_loc':desti_location_name,
					'product_name':gate_pass_line.description,
					'product_qty':gate_pass_line.product_qty,
					'product_uom':gate_pass_line.product_qom.name}
				product_list.append(dict)	
		
		data['other'] ={'source_location':source_location_name,'desti_location':desti_location_name} 
		data['ids'] = product_list
		data['form'] = self.read([], ['start_date', 'end_date'])[0]
		return self.env['report'].get_action(self, 'stock_gatepass.report_gate_pass_qweb', data=data)
		