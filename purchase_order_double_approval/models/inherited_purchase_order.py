from openerp import api, fields, models
from openerp import _
from openerp.exceptions import Warning

class InheritedPurchaseOrder(models.Model):
	_inherit = 'purchase.order'

	STATE_SELECTION = [
        ('draft', 'Draft PO'),
        ('sent', 'RFQ'),
        ('bid', 'Bid Received'),
        ('confirmed1', 'Waiting Approval-1'),
        ('confirmed', 'Waiting Approval-2'),
        ('approved', 'Purchase Confirmed'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ]
	
	state= fields.Selection(STATE_SELECTION, 'Status', readonly=True,
                                  help="The status of the purchase order or the quotation request. "
                                       "A request for quotation is a purchase order in a 'Draft' status. "
                                       "Then the order has to be confirmed by the user, the status switch "
									   "to 'Confirmed 1'. Then the supplier must confirm-1 the order to change "
                                       "to 'Confirmed'. Then the supplier must confirm the order to change "
                                       "the status to 'Approved'. When the purchase order is paid and "
                                       "received, the status becomes 'Done'. If a cancel action occurs in "
                                       "the invoice or in the receipt of goods, the status becomes "
                                       "in exception.",
                                  select=True, copy=False)
	
	@api.multi
	def wkf_approval_1st(self):
		print '----self---',self
		self.state = 'confirmed1'
	
	def wkf_confirm_order_abc(self, cr, uid, ids, context=None):
	    todo = []
	    for po in self.browse(cr, uid, ids, context=context):
	        if not any(line.state != 'cancel' for line in po.order_line):
	            raise osv.except_osv(_('Error!'),_('You cannot confirm a purchase order without any purchase order line.'))
	        if po.invoice_method == 'picking' and not any([l.product_id and l.product_id.type in ('product', 'consu') and l.state != 'cancel' for l in po.order_line]):
	            raise osv.except_osv(
	                _('Error!'),
	                _("You cannot confirm a purchase order with Invoice Control Method 'Based on incoming shipments' that doesn't contain any stockable item."))
	        for line in po.order_line:
	            if line.state=='draft':
	                todo.append(line.id)        
	    self.pool.get('purchase.order.line').action_confirm(cr, uid, todo, context)
	    for id in ids:
	        self.write(cr, uid, [id], {'state' : 'confirmed', 'validator' : uid})
	    return True
# 	@api.multi
# 	def purchase_confirm_1(self):
# 		print '----self 1---',self
# 		self.state = 'confirmed'