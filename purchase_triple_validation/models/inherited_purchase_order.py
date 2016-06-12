from openerp import api, fields, models
class InheritedPurchaseOrder(models.Model):
	_inherit = "purchase.order"

	date_validate=fields.Date('Date Validated', readonly=1, select=True, help="Date on which purchase order has been approved")
	
	state = fields.Selection([
		 ('draft', 'Draft PO'),
		 ('sent', 'RFQ Sent'),
		 ('to approve', 'To Approve'),
		 ('to_sec_approve', 'To Approve'),
		 ('purchase', 'Purchase Order'),
		 ('done', 'Done'),
		 ('cancel', 'Cancelled')
		 ], string='Status', readonly=True, select=True, copy=False, default='draft', track_visibility='onchange')
	 
	
	@api.multi
	def first_approve(self):
	    for order in self:
	        order._add_supplier_to_product()
	        # Deal with double validation process
	        if order.company_id.po_double_validation == 'one_step'\
	                or (order.company_id.po_double_validation == 'two_step'\
	                    and order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id))\
	                or (order.company_id.po_double_validation == 'three_step'\
	                    and order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.po_triple_validation_amount, order.currency_id)):
	            order.button_approve()
	        else:
	            order.write({'state': 'to_sec_approve'})
	    return {}
	
	@api.multi
	def second_approve(self):
		self.state = "purchase"
		self.date_validate = fields.Date.today()
		self._create_picking()
		return {}