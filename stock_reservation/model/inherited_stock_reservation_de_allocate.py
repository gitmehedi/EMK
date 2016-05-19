from openerp import api, fields, models
from openerp import _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class InheritedStockReservation(models.Model):
	_inherit = 'stock.reservation'
	_description = 'Stock De-Allocation'
	
	stock_reservation_line_ids = fields.One2many('stock.reservation.line', 'stock_reservation_id', string="Stock Reservation", readonly=True, states={'draft':[('readonly', False)],'generate':[('readonly',False)]}, copy=True)
	
	@api.multi
	@api.onchange('analytic_account_id', 'warehouse_id')
	def onchange_analytic_warehouse(self):
		obj_reservation = ''
		if self.analytic_account_id and self.warehouse_id:
			obj_reservation = self.env['stock.reservation'].search([['analytic_account_id','=',self.analytic_account_id.id],['warehouse_id','=',self.warehouse_id.id]], limit=1)
			if self.allocate_flag == 2:
				self.source_loc_id = obj_reservation.source_loc_id.id
			if self.allocate_flag == 3:
				self.source_loc_id = obj_reservation.source_loc_id.id
	
	@api.multi
	def action_generate_line(self):
		if self.analytic_account_id and self.warehouse_id:
			obj_reservation = self.env['stock.reservation'].search([['analytic_account_id','=',self.analytic_account_id.id],['warehouse_id','=',self.warehouse_id.id]], limit=1)
			query = '''
				SELECT product_id, sum(quantity) AS quantity FROM(
					SELECT srl.product_id, sum(srl.quantity) AS quantity  FROM stock_reservation sr
						LEFT JOIN stock_reservation_line srl on sr.id = srl.stock_reservation_id
						where sr.allocate_flag = 1 
						AND sr.analytic_account_id = %s 
						AND sr.warehouse_id = %s 
						AND sr.state='reserve'
						GROUP BY srl.product_id
					UNION ALL
					SELECT srl.product_id, sum(srl.quantity*-1) AS quantity  FROM stock_reservation sr
						LEFT JOIN stock_reservation_line srl on sr.id = srl.stock_reservation_id
						where sr.allocate_flag = 2 
						AND sr.analytic_account_id = %s 
						AND sr.warehouse_id = %s 
						AND sr.state='release'
						GROUP BY srl.product_id	
					UNION ALL
					SELECT srl.product_id, sum(srl.quantity) AS quantity  FROM stock_reservation sr
						LEFT JOIN stock_reservation_line srl on sr.id = srl.stock_reservation_id
						where sr.allocate_flag = 3 
						AND sr.analytic_account_id = %s 
						AND sr.warehouse_id = %s 
						AND sr.state='release'
						GROUP BY srl.product_id
					)generate_line
				GROUP BY product_id
			''' % (self.analytic_account_id.id, self.warehouse_id.id,self.analytic_account_id.id, self.warehouse_id.id,self.analytic_account_id.id, self.warehouse_id.id)
# 			self.ensure_one()

			res_ext = self.env.cr.execute(query)
			result = self.env.cr.dictfetchall()
			res_vals = []
			res_line_obj = self.env['stock.reservation.line']
			for line in result:
				product_id = self.env['product.product'].search([['id','=',line['product_id']]])
				uom_category_id=product_id.uom_id.category_id.id
				uom_id=product_id.uom_id.id
 				if self.allocate_flag == 2:
	 				res_vals = {
	 				    'analytic_account_id':self.analytic_account_id.id,
	 				    'product_id': line['product_id'],
	 				    'stock_reservation_id': self.id,
	 				    'uom_category':product_id,
	 				    'uom':uom_id,
	 				    'quantity':line['quantity'] or 0,
	 				    'allocate_qty':line['quantity'] or 0,
	 				    
	 				}
	 			if self.allocate_flag == 3:
	 				res_vals = {
 				    'analytic_account_id':self.analytic_account_id.id,
 				    'product_id': line['product_id'],
 				    'stock_reservation_id': self.id,
 				    'uom_category':product_id,
 				    'uom':uom_id,
 				    'quantity':line['quantity'] or 0,
 				    'allocate_qty':line['quantity'] or 0,
 				    
 				}
 				if(res_vals['allocate_qty'] > 0):
					res_line_obj.create(res_vals)
					self.write({'state':'generate'})
					
	 			

	@api.multi
	def action_re_generate_line(self):
		if self.analytic_account_id and self.warehouse_id:
			obj_reservation = self.env['stock.reservation'].search([['analytic_account_id','=',self.analytic_account_id.id],['warehouse_id','=',self.warehouse_id.id]], limit=1)
			query = '''
				SELECT product_id, sum(quantity) AS quantity FROM(
					SELECT srl.product_id, sum(srl.quantity) AS quantity  FROM stock_reservation sr
						LEFT JOIN stock_reservation_line srl on sr.id = srl.stock_reservation_id
						where sr.allocate_flag = 1 
						AND sr.analytic_account_id = %s 
						AND sr.warehouse_id = %s 
						AND sr.state='reserve'
						GROUP BY srl.product_id
					UNION ALL
					SELECT srl.product_id, sum(srl.quantity*-1) AS quantity  FROM stock_reservation sr
						LEFT JOIN stock_reservation_line srl on sr.id = srl.stock_reservation_id
						where sr.allocate_flag = 2 
						AND sr.analytic_account_id = %s 
						AND sr.warehouse_id = %s 
						AND sr.state='release'
						GROUP BY srl.product_id
					UNION ALL
					SELECT srl.product_id, sum(srl.quantity) AS quantity  FROM stock_reservation sr
						LEFT JOIN stock_reservation_line srl on sr.id = srl.stock_reservation_id
						where sr.allocate_flag = 3 
						AND sr.analytic_account_id = %s 
						AND sr.warehouse_id = %s 
						AND sr.state='release'
						GROUP BY srl.product_id	
					)generate_line
				GROUP BY product_id
			''' % (self.analytic_account_id.id, self.warehouse_id.id,self.analytic_account_id.id, self.warehouse_id.id,self.analytic_account_id.id, self.warehouse_id.id)
# 			self.ensure_one()
			res_ext = self.env.cr.execute(query)
			result = self.env.cr.dictfetchall()
			res_vals = []
			res_line_obj = self.env['stock.reservation.line']
			for line in result:
				product_id = self.env['product.product'].search([['id','=',line['product_id']]])
				uom_category_id=product_id.uom_id.category_id.id
				uom_id=product_id.uom_id.id
 				if self.allocate_flag == 2:
	 				res_vals = {
	 				    'analytic_account_id':self.analytic_account_id.id,
	 				    'product_id': line['product_id'],
	 				    'stock_reservation_id': self.id,
	 				    'uom_category':product_id,
	 				    'uom':uom_id,
	 				    'quantity':line['quantity'] or 0,
	 				    'allocate_qty':line['quantity'] or 0,
	 				    
	 				}
	 			if self.allocate_flag == 3:
	 				res_vals = {
	 				    'analytic_account_id':self.analytic_account_id.id,
	 				    'product_id': line['product_id'],
	 				    'stock_reservation_id': self.id,
	 				    'uom_category':product_id,
	 				    'uom':uom_id,
	 				    'quantity':line['quantity'] or 0,
	 				    'allocate_qty':line['quantity'] or 0,
	 				    
	 				}
				
 				if(res_vals['allocate_qty'] > 0):
					res_line_obj.write(res_vals)
					self.write({'state':'generate'})
			
	@api.multi
	def action_release(self):
		self.state = 'release'	
		
	'''			
	@api.multi
	def action_release(self):
	    obj_stock_picking = self.env['stock.picking']
	    pick_vals = {
	            'picking_type_id': self.env['stock.picking.type'].search([('name', '=', 'Stock Reservation')], limit=1).id,
	            'state':'assigned',
	            'date':fields.Datetime.now(),
	            'stock_reservation_id':self.id
	            }
	    picking_id=obj_stock_picking.create(pick_vals)
	    
	    self.state = 'release'
	    if picking_id and self.stock_reservation_line_ids:
	        for res in self:
	            for line in res.stock_reservation_line_ids:
	                    
	                obj_stock_move = self.env['stock.move']
	                if self.allocate_flag == 2:
		                move_vals = {
		                    'name': line.product_id.name,
		                    'date':fields.Datetime.now(),
		                    'date_expected': fields.Datetime.now(),
		                    'picking_id': picking_id.id,
		                    'picking_type_id': self.env['stock.picking.type'].search([('name', '=', 'Stock Reservation')], limit=1).id,
		                    'product_id': line.product_id.id,
		                    'product_uom':line.uom.id,
		                    'price_unit':line.product_id.standard_price or 0.0,
		                    'product_uom_qty': line.quantity,
		                    'location_id': self.source_loc_id.id,
		                    'location_dest_id': self.analytic_resv_loc_id.id,
		                    'state':'assigned',
		                    
		                }
	                if self.allocate_flag == 3:
	                	move_vals = {
		                    'name': line.product_id.name,
		                    'date':fields.Datetime.now(),
		                    'date_expected': fields.Datetime.now(),
		                    'picking_id': picking_id.id,
		                    'picking_type_id': self.env['stock.picking.type'].search([('name', '=', 'Stock Reservation')], limit=1).id,
		                    'product_id': line.product_id.id,
		                    'product_uom':line.uom.id,
		                    'price_unit':line.product_id.standard_price or 0.0,
		                    'product_uom_qty': line.quantity,
		                    'location_id': self.analytic_resv_loc_id.id,
		                    'location_dest_id': self.analytic_resv_loc_id.id,
		                    'state':'assigned',
		                }
	                move_id  = obj_stock_move.create(move_vals)
	                
	'''               
	
class InheritedStockReservationLine(models.Model):
	_inherit = 'stock.reservation.line'
	
	allocate_qty = fields.Float(digits=(20, 2),string='Reservation Qty', default=0.0)               
	
	
	@api.one
	@api.onchange('quantity')
	def onchange_quantity(self):
		if self.stock_reservation_id.allocate_flag != 1 and self.quantity and self.allocate_qty and self.quantity > self.allocate_qty:
# 			print '---------self.allocate_qty------',self.allocate_qty
# 			print '---------self.quantity------',self.quantity
			self.quantity = self.allocate_qty
# 			res = {
#             'value': {
# 				#This sets the total price on the field standard_price.
# 		                'quantity': self.allocate_qty
# 			      }
# 			}
			#Return the values to update it in the view.
# 			print '---------res------',res
			raise Warning(_('Quantity can not be Greater than Allocate Qty'))
# 			raise except_orm('res','Quantity can not be Greater than Allocate Qty')
			
		
	@api.multi
	def write(self, vals):
		if self.stock_reservation_id.allocate_flag != 1:
			if 'allocate_qty' in vals:
				allocate_qty = vals['allocate_qty']
			else:
				allocate_qty = self.allocate_qty
			quantity = vals.get('quantity', False)
			if quantity > allocate_qty:
				raise Warning(_('Quantity can not be Greater than Allocate Qty')) 
		return super(InheritedStockReservationLine, self).write(vals)	