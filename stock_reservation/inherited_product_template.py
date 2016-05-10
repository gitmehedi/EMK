from openerp import api, fields, models

class InheritedProductTemplate(models.Model):
	_inherit = 'product.template'
	
	reserve_qty = fields.Float(digits=(20, 2), string='Reservation Quantity', compute="_computed_reservation_qty",  default=20.0)
	

	
	@api.depends('name')
	def _computed_reservation_qty(self):
		for product_tm in self:
			print '------product---',product_tm.id
			product_tm.reserve_qty = 0.0
# 			res_obj = self.env['reservation.quant'].search([['product_id','=',product.id]])
# 			product.reserve_qty = res_obj.reserve_quantity
			if product_tm.id:
				query = '''
					SELECT COALESCE(sum(rq.reserve_quantity),0) AS reserve_quantity
						 FROM reservation_quant rq
						 LEFT JOIN product_product pp on (rq.product_id=pp.id)
						 LEFT JOIN product_template pt on (pp.product_tmpl_id=pt.id)
						WHERE pt.id = %s
						GROUP BY pt.id
				'''%(product_tm.id) 

				res_ext = self.env.cr.execute(query)
				result = self.env.cr.dictfetchone()
				if result:
					product_tm.reserve_qty = result['reserve_quantity']
	
	@api.multi
	def action_open_reservation(self,context=None):
	    products = self._get_products()
	    result = self._get_act_window_dict('stock_reservation.action_reservation_quant_tree')
	    result['domain'] = "[('product_id','in',[" + ','.join(map(str, products)) + "])]"
	    result['context'] = "{'search_default_productgroup': 1, 'search_default_analyticgroup': 1}"
	    return result			