from openerp import api, fields, models

class InheritedProductTemplate(models.Model):
	_inherit = 'product.template'
	
	reserve_qty = fields.Float(digits=(20, 2), string='Reservation Quantity', compute="_computed_reservation_qty",  default=20.0)
	

	
	@api.depends('name')
	def _computed_reservation_qty(self):
		for product in self:
			print '------product---',product
# 			res_obj = self.env['reservation.quant'].search([['product_id','=',product.id]])
# 			product.reserve_qty = res_obj.reserve_quantity
			
			query = '''
				SELECT COALESCE(sum(rq.reserve_quantity),0) AS reserve_quantity  FROM reservation_quant rq
					WHERE rq.product_id = %s
					GROUP BY rq.product_id
			'''%(product.id) 
			res_ext = self.env.cr.execute(query)
			result = self.env.cr.dictfetchone()
			product.reserve_qty = result['reserve_quantity']