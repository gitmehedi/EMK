from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator


class SalesContractDetails(models.Model):
    _name = 'sales.contract.details'
    
    # Relationship fields
    sales_contract_id = fields.Many2one('sales.contract', delegate=True, ondelete="cascade")
    
    po_related = fields.Many2one('buyer.work.order', ondelete="cascade", string="PO's to Relate", required=True,
                               domain=[('state', '=', 'confirm')])
    tagged_po = fields.Many2one('buyer.work.order', ondelete="cascade",string="Tagged PO", required=True,
                               domain=[('state', '=', 'confirm')])
    
    
    
    # All function which process data and operation
    
    
    



     
    
    


        
        
            
    
