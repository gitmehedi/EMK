from openerp import api, fields, models


class InheritedPurchaseOrderLine(models.Model):
	_inherit = 'purchase.order.line'

	product_id = fields.Many2one('product.template', 'Product', domain=[('type','!=','service')])
	receive_qty = fields.Float(string='Receive Quantity',default="0.0")
		
	def name_get(self, cr, uid, ids, context):
		res = []
		if not len(ids):
		  return []
		for record in self.browse(cr, uid, ids, context=context):
		    # As I understood prj_id it is many2one field. For example I set name of prj_id
			res.append((record.id, record.product_id.name))
		return res
