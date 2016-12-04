from openerp import api, fields, models


class InheritedStockInventory(models.Model):
	_inherit = 'stock.inventory'
	
	
	def _get_inventory_lines(self, cr, uid, inventory, context=None):
		location_obj = self.pool.get('stock.location')
		product_obj = self.pool.get('product.product')
		location_ids = location_obj.search(cr, uid, [('id', 'child_of', [inventory.location_id.id])], context=context)

 		domain = ' location_id in %s'
		args = (tuple(location_ids),)
		if inventory.partner_id:
			domain += ' and owner_id = %s'
			args += (inventory.partner_id.id,)
		if inventory.lot_id:
			domain += ' and lot_id = %s'
			args += (inventory.lot_id.id,)
		if inventory.product_id:
			domain += ' and product_id = %s'
			args += (inventory.product_id.id,)
		if inventory.package_id:
			domain += ' and package_id = %s'
			args += (inventory.package_id.id,)

		cr.execute('''
		   SELECT product_id, sum(qty) as product_qty, location_id, lot_id as prod_lot_id, package_id, owner_id as partner_id
		   FROM stock_quant WHERE''' + domain + '''
		   GROUP BY product_id, location_id, lot_id, package_id, partner_id
		''', args)
		vals = []
		for product_line in cr.dictfetchall():
			# replace the None the dictionary by False, because falsy values are tested later on
			for key, value in product_line.items():
				if not value:
					product_line[key] = False
			product_line['inventory_id'] = inventory.id
			product_line['theoretical_qty'] = product_line['product_qty']
			if product_line['product_id']:
				product = product_obj.browse(cr, uid, product_line['product_id'], context=context)
				product_line['product_uom_id'] = product.uom_id.id
			vals.append(product_line)
		return vals

	
class InheritedStockInventoryLine(models.Model):
	_inherit = "stock.inventory.line"
	
	def onchange_createline(self, cr, uid, ids, location_id=False, product_id=False, uom_id=False, package_id=False, prod_lot_id=False, partner_id=False, company_id=False, context=None):
		quant_obj = self.pool["stock.quant"]
		uom_obj = self.pool["product.uom"]
		res = {'value': {}}
		# If no UoM already put the default UoM of the product

		if product_id:
			product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
  			
			uom = self.pool['product.uom'].browse(cr, uid, uom_id, context=context)
 			
			uom_id = product.uom_id.id
			res['value']['product_uom_id'] = uom_id
			if product.uom_id.category_id.id != uom.category_id.id:
				res['value']['product_uom_id'] = product.uom_id.id
				res['domain'] = {'product_uom_id': [('category_id', '=', product.uom_id.category_id.id)]}
  				
		# Calculate theoretical quantity by searching the quants as in quants_get
		if product_id and location_id:
			product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
			if not company_id:
				company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
			dom = [('company_id', '=', company_id), ('location_id', '=', location_id), ('lot_id', '=', prod_lot_id),
						('product_id', '=', product_id), ('owner_id', '=', partner_id), ('package_id', '=', package_id)]
			quants = quant_obj.search(cr, uid, dom, context=context)
			th_qty = sum([x.qty for x in quant_obj.browse(cr, uid, quants, context=context)])
			if product_id and uom_id and product.uom_id.id != uom_id:
				th_qty = uom_obj._compute_qty(cr, uid, product.uom_id.id, th_qty, uom_id)
			res['value']['theoretical_qty'] = th_qty
			res['value']['product_qty'] = th_qty
		return res
	
	
# 	def onchange_createline(self, cr, uid, ids, location_id=False, product_id=False, uom_id=False, package_id=False, prod_lot_id=False, partner_id=False, company_id=False, context=None):
# 		if product_id:
# 			product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
# 			uom_id = product.uom_id.id
# 			print "uom_id============",uom_id
#  			
# 		return super(InheritedStockInventoryLine, self).onchange_createline(cr, uid, ids, location_id, product_id, uom_id, package_id, prod_lot_id, partner_id, company_id, context)

