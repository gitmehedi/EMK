from openerp import api, fields, models

class InheritedProductProduct(models.Model):
	_inherit = 'product.product'
	
	reserve_qty = fields.Float(digits=(20, 2), string='Reservation Quantity', compute="_computed_reservation_qty",  default=20.0)
	

	
	@api.depends('name')
	def _computed_reservation_qty(self):
		for product in self:
			product.reserve_qty = 0.0
			if product.id:
				query = '''
					SELECT COALESCE(sum(rq.reserve_quantity),0) AS reserve_quantity
						 FROM reservation_quant rq
						WHERE rq.product_id = %s
						GROUP BY rq.product_id
				'''%(product.id) 
				res_ext = self.env.cr.execute(query)
				result = self.env.cr.dictfetchone()
				if result:
					product.reserve_qty = result['reserve_quantity']
	
	
	@api.multi
	def product_reservation(self):
		obj_pro_temp=self.env['product.template']
		result = obj_pro_temp._get_act_window_dict('stock_reservation.action_reservation_quant_tree')
		result['domain'] = "[('product_id','='," + str(self.id) + ")]"
		result['context'] = "{'search_default_productgroup': 1, 'search_default_analyticgroup': 1}"
		return result			