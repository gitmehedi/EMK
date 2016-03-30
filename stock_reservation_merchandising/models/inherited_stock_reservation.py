from openerp import api, fields, models
from openerp import _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class InheritedStockReservation(models.Model):
	_inherit = 'stock.reservation'
	_description = 'Stock Allocation'
	
	
	work_order_id = fields.Many2one('buyer.work.order',"Work Order", compute='_computed_work_order', required=True,readonly=True, states={'draft':[('readonly', False)]})
	bom_id = fields.Many2one('bom.consumption',"Bill of Materials", required=True, compute='_computed_bom',readonly=True, states={'draft':[('readonly', False)]})
	set_product = fields.Many2one('product.product', string="Product")
	
	#@api.multi
	@api.depends('analytic_account_id')
	def _computed_work_order(self):
		if self.analytic_account_id:
			self.work_order_id = self.work_order_id.search([['name','=',self.analytic_account_id.name]])
			print '+++++++++===after .work_order_id======',self.work_order_id
	
	#@api.multi
	@api.depends('analytic_account_id')
	def _computed_bom(self):
		ctx = self.env.context.copy()
		
		
# 		context = self._context.copy()
# 		print "========context==========",context
# 		context.update({'product_ids':[3,4,5]})
# 		print "========context==========",context
# #     	new_obj = self.with_context(context)
		print "========context==========",self._context

		res = {}
		val = {}
		list_data = []
		new_obj = {}
		if self.analytic_account_id:
			
			self.bom_id = self.bom_id.search([['export_po_id','=',self.work_order_id.id]])
			print '+++++++++===after .bom_id======',self.bom_id
			ctx.update({'default_bom_id':self.bom_id.id})
			new_obj = self.with_context({'default_bom_id': self.bom_id.id})
# 			new_obj = self.env['stock.reservation'].with_context({}, bom_id=self.bom_id.id)
			print "========44==========",self._context
# 			print "========45==========",ctx
			print "========46==========",new_obj._context
		return new_obj
# 			if self.bom_id:
# 				print '+++++++++===after .bom#################======',self.bom_id.yarn_ids
# 				
# 		# 				val.update({'set_product': [ product.product_id for product in self.bom_id.yarn_ids ]})
# 		# 				print '+++++++++++ val', val
# 		# 				print '+++++++++++ set_product', self.set_product
# 		# 				
# 		#         		return {'value': val}
# 				
# 				
# 				
# 				for product in self.bom_id.yarn_ids:
# 					print '------------product------',product.product_id
# 					
# 					list_data.append(product.product_id.id)
# 				print '--------result---',list_data
# 				val['set_product'] = list_data
# 				print '--------val---',val
# 				return {'value': val}
			
# 				res = {'domain': {'set_product':[]}}
# 				res['domain'] = {
# 				        'set_product':[('id', 'in', [result])]       
# 				}
# 				print '--------res---',res
# 				return res
					

	
# 	@api.multi
# 	@api.depends('analytic_account_id')
# 	def _computed_set_product(self):
# 		if self.analytic_account_id:
# 			val = {}
# 			res = {}
# 			self.bom_id = self.bom_id.search([['export_po_id','=',self.work_order_id.id]])
# 			print '+++++++++===after .bom_id======',self.bom_id
# 			if self.bom_id:
# 				print '+++++++++===after .bom#################======',self.bom_id.yarn_ids
# # 				for product in self.bom_id.yarn_ids:
# # 					print '------------product------',product.product_id
# # 					val.update({'set_product': product.product_id})
# # 					return {'value': val}
# 				val.update({'set_product': [ product.product_id for product in self.bom_id.yarn_ids ]})
# 				print '------------val------',val
# 				res['domain'] = {'set_product': [('lot_additional_fields', 'in', ids)]}
#         	return res
				

# 		val = {}
#         if not standard_id:
#             return {}
#         student_obj = self.pool.get('fci.standard')
#         student_data = student_obj.browse(cr, uid, standard_id, context=context)
#         val.update({'group_id': student_data.groups_ids.id})
#         return {'value': val}		
# 	@api.one
# 	@api.onchange('stock_reservation_line_ids')
# 	def _get_product_data(self):
# 		print '----------=41======',self.bom_id
# 		if self.bom_id:
# 			print '+++++++++===43#################======',self.bom_id
# 			for product in self.bom_id.yarn_ids:
# 				print '------------product------',product.product_id
# 				
# 				for sr in self:
# 					print '+++++++ 48===',sr.stock_reservation_line_ids
# 				
# 					for line in sr.stock_reservation_line_ids:
# 						line.product_id =  product.product_id
# 						print '+++++++++===aline.product_id #################======',line.product_id
	        
			
class InheritedStockReservationLine(models.Model):
	_inherit = 'stock.reservation.line'
	
	
	def _get_default_product(self):
	    ctx = self.env['stock.reservation']
	    print '++++++++++++++133-----------',ctx
	
	def _default_sessions(self):
		return self.env['stock.reservation'].browse(self._context.get('active_ids'))	 
	
	def _get_default_product_222(self):
		products = []
		print '---------125', self.env.context
		ctx = self.env['stock.reservation']._context
		print '++++++==127==',ctx
		print '---128--',self._context
		print '----129--',self._context.get('field_parent')
		print '-------self.bom_id----------',self.bom_id
		for line in self.bom_id.yarn_ids:
			products.append(line.product_id.id)
		print '-------products----------',products
   		return products[0]
	
	work_order_id = fields.Many2one(string='Work Order',
								related='stock_reservation_id.work_order_id')
	bom_id = fields.Many2one(string='Bill of Materials',
							related='stock_reservation_id.bom_id')
	product_id = fields.Many2one('product.product', string="Product", default=_get_default_product)
	
	
	
	
# 	@api.model
# 	def _get_default_product(self):
# 		print '---self--',self.stock_reservation_id.analytic_account_id
# 		print 'context ',self._context.get('analytic_account_id',False)
# 		for line in self:
# 			print 'stock_reservation_id----------',line.stock_reservation_id
# 			print 'bom----------',line.stock_reservation_id.bom_id
# 			print 'abc'
	
# 	product_id = fields.Many2one('product.product', default=lambda self: self._get_default_product(), string="Product")
# 	product_id = fields.Many2one('product.product', string="Product")
# 	product_id = fields.Many2one('product.product', compute='_computed_product', store=True, string="Product")
# 	product_id = fields.Many2one('product.product', 'Product',
#                                  domain="[('id','in',parent.set_product)]",
#                                  change_default=True)
# 	product_id = fields.Many2one('product.product', 'Product',
#                                  domain="[('product_tmpl_id.product','=',parent.product)]",
#                                  change_default=True, readonly=True,
#                                  states={'draft': [('readonly', False)]},
#                                  ondelete='restrict')
	
	
# 	@api.multi
# 	@api.depends('product_id')
# 	def _computed_product(self):
# 		print '---self--',self.stock_reservation_id.warehouse_id
# 		for line in self:
# 			print 'stock_reservation_id----------',line.stock_reservation_id
# 			print 'bom----------',line.stock_reservation_id.bom_id
# 			print 'abc'    
	

			
		