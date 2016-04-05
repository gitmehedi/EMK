from openerp import api, fields, models
from openerp import _
from openerp.exceptions import Warning

class InheritedPurchaseOrder(models.Model):
	_inherit = 'purchase.order'

	STATE_SELECTION = [
        ('draft', 'Draft PO'),
        ('sent', 'RFQ'),
        ('bid', 'Bid Received'),
        ('confirmed', 'Waiting Approval-1'),
        ('confirmed2', 'Waiting Approval-2'),
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
	def wkf_approval_2nd(self):
		print '----self---',self
		self.state = 'confirmed2'
	
	
# 	@api.multi
# 	def purchase_confirm_1(self):
# 		print '----self 1---',self
# 		self.state = 'confirmed'