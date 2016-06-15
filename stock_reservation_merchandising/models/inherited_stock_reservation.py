from openerp import api, fields, models
from openerp import _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class InheritedStockReservation(models.Model):
	_inherit = 'stock.reservation'
	_description = 'Stock Allocation'
	
	
	work_order_id = fields.Many2one('sale.order',"Work Order", compute='_computed_work_order', readonly=True, states={'draft':[('readonly', False)]})
	bom_id = fields.Many2one('bom.consumption',"Bill of Materials", compute='_computed_bom',readonly=True, states={'draft':[('readonly', False)]})
# 	set_product = fields.Many2one('product.product', string="Product")
	
	#@api.multi
	@api.depends('analytic_account_id')
	def _computed_work_order(self):
		if self.analytic_account_id:
			self.work_order_id = self.work_order_id.search([['name','=',self.analytic_account_id.name]])

	#@api.multi
	@api.depends('analytic_account_id')
	def _computed_bom(self):
		ctx = self.env.context.copy()
		new_obj = {}
		if self.analytic_account_id:
			
			self.bom_id = self.bom_id.search([['export_po_id','=',self.work_order_id.id]])
			ctx.update({'default_bom_id':self.bom_id.id})
			new_obj = self.with_context({'default_bom_id': self.bom_id.id})
		return new_obj

			
class InheritedStockReservationLine(models.Model):
	_inherit = 'stock.reservation.line'
	
	
	def _get_default_product(self):
	    ctx = self.env['stock.reservation']
	
	def _default_sessions(self):
		return self.env['stock.reservation'].browse(self._context.get('active_ids'))	 
	
	def _get_default_product_222(self):
		products = []
		ctx = self.env['stock.reservation']._context
		for line in self.bom_id.yarn_ids:
			products.append(line.product_id.id)
   		return products[0]
	
	work_order_id = fields.Many2one(string='Work Order',
								related='stock_reservation_id.work_order_id')
	bom_id = fields.Many2one(string='Bill of Materials',
							related='stock_reservation_id.bom_id')
	product_id = fields.Many2one('product.product', string="Product", default=_get_default_product)

		