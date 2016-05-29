from openerp import api, fields, models
from openerp import _
from openerp.exceptions import Warning

class InheritedPurchaseRequisition(models.Model):
	_inherit = 'purchase.requisition'

	state = fields.Selection([('draft', 'Draft'), ('in_progress', 'Confirmed'),('approved', 'Approved'),
                                   ('open', 'Bid Selection'), ('done', 'PO Created'),
                                   ('close', 'Close'),('cancel', 'Cancelled')],
                                  'Status', required=True, readonly=True, states={'draft': [('readonly', False)]},
                                  copy=False)
	
	@api.multi
	def action_approved(self):
		self.state = "approved"
	
	@api.multi
	def action_close(self):
		self.state = "close"
		
	@api.one
	def open_bid(self):
		self.state = "open"	
	
	@api.multi
	def generate_po(self, context=None):
	    """
	    Generate all purchase order based on selected lines, should only be called on one tender at a time
	    """
	    po = self.env['purchase.order']
	    poline = self.env['purchase.order.line']
	    id_per_supplier = {}
	    for tender in self.browse(self.ids):
	        if tender.state == 'done':
	           	raise Warning(_('You have already generate the purchase order(s).'))
	
	        confirm = False
	        #check that we have at least confirm one line
	        for po_line in tender.po_line_ids:
	            if po_line.state == 'confirmed':
	                confirm = True
	                break
	        if not confirm:
	        	raise Warning(_('You have no line selected for buying.'))
	        #check for complete RFQ
	        for quotation in tender.purchase_ids:
	            if (self.check_valid_quotation(quotation)):
	                #use workflow to set PO state to confirm
	                po.signal_workflow('purchase_confirm')
	        #get other confirmed lines per supplier
	        for po_line in tender.po_line_ids:
	            #only take into account confirmed line that does not belong to already confirmed purchase order
	            if po_line.state == 'confirmed' and po_line.order_id.state in ['draft', 'sent', 'bid']:
	                if id_per_supplier.get(po_line.partner_id.id):
	                    id_per_supplier[po_line.partner_id.id].append(po_line)
	                else:
	                    id_per_supplier[po_line.partner_id.id] = [po_line]
	
	        #generate po based on supplier and cancel all previous RFQ
	        ctx = dict(context or {}, force_requisition_id=True)
	        for supplier, product_line in id_per_supplier.items():
	            #copy a quotation for this supplier and change order_line then validate it
	            quotation_id = po.search([('requisition_id', '=', tender.id), ('partner_id', '=', supplier)], limit=1)[0]
	            vals = self._prepare_po_from_tender(tender)
	            new_po = po.copy(quotation_id, default=vals)
	            #duplicate po_line and change product_qty if needed and associate them to newly created PO
	            for line in product_line:
	                vals = self._prepare_po_line_from_tender(tender, line, new_po)
	                poline.copy(line.id, default=vals)
	            #use workflow to set new PO state to confirm
	            po.signal_workflow([new_po], 'purchase_confirm')
	
	        #cancel other orders
	        self.cancel_unconfirmed_quotations(tender)
	        #set tender to state done
	        self.signal_workflow('done')
 	      	self.state = "done"
	    return True
	
	 
class InheritPurchaseOrder(models.Model):
    _inherit = "purchase.order"

    requisition_id =fields.Many2one('purchase.requisition', 'Purchase Requisition', domain=[('state','=','approved')], copy=False)
