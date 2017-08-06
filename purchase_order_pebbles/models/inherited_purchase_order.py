from openerp import api, fields, models


class InheritedPurchaseOrder(models.Model):
	_inherit = 'purchase.order'

	


	def action_picking_create(self, cr, uid, ids, context=None):
		
		print "#################self#########################", self
# 		raise osv.except_osv(_('Error!'),_('You Line cannot confirm a purchase order without any purchase order line.'))
		return True

	def action_invoice_create(self, cr, uid, ids, context=None):
		"""Generates invoice for given ids of purchase orders and links that invoice ID to purchase order.
		:param ids: list of ids of purchase orders.
		:return: ID of created invoice.
		:rtype: int
		"""

	def action_purchase_done(self, cr, uid, ids, context=None):

		self.write(cr, uid, ids, {'state': 'done'}, context=context)
		

