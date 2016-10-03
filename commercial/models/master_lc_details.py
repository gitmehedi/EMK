from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator


class MasterLCDetails(models.Model):
    _name = 'master.lc.details'
    
    # Relationship fields
    master_lc_id = fields.Many2one('master.lc', delegate=True, ondelete="cascade")
    
    po_related = fields.Many2one('buyer.work.order', ondelete="cascade", string="PO's to Relate", required=True,
                               domain=[('state', '=', 'confirm')])
    tagged_po = fields.Many2one('buyer.work.order', ondelete="cascade", string="Tagged PO", required=True,
                               domain=[('state', '=', 'confirm')])
    
    
    
    # All function which process data and operation
    
    
    



     
    
    


        
        
            
    
