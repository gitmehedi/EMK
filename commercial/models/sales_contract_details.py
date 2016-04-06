from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator


class SalesContractDetails(models.Model):
    _name = 'sales.contract.details'
    
    # Relationship fields
    sales_contract_id = fields.Many2one('sales.contract', ondelete="cascade")
    
    po_related_id = fields.Many2one('buyer.work.order', ondelete="cascade", string="PO's to Relate", required=True)
    tagged_po_id = fields.Many2one('buyer.work.order', ondelete="cascade", string="Tagged PO", required=True)
    
    
    
    # All function which process data and operation
    
    
    



     
    
    


        
        
            
    
