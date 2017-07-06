from openerp import api, fields, models


class InheritedPurchaseOrderLine(models.Model):
	_inherit = 'purchase.order.line'

	product_id = fields.Many2one('product.template', 'Product', domain=[('type','!=','service')])
	receive_qty = fields.Float(string='Receive Quantity',default="0.0")

	def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
							partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
							name=False, price_unit=False, state='draft', context=None):

		if product_id:
			prod_pool = self.pool.get('product.product')
			product_id = prod_pool.search(cr, uid, [('product_tmpl_id','=',product_id)])[0]


			return super(InheritedPurchaseOrderLine, self).onchange_product_id(cr, uid, ids,pricelist_id, product_id, qty, uom_id,
							partner_id, date_order, fiscal_position_id, date_planned,name, price_unit, state, context)
		
	def name_get(self, cr, uid, ids, context):
		res = []
		if not len(ids):
		  return []
		for record in self.browse(cr, uid, ids, context=context):
		    # As I understood prj_id it is many2one field. For example I set name of prj_id
			res.append((record.id, record.product_id.name))
		return res
