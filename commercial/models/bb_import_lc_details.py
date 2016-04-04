from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator


class BBImportLCDetails(models.Model):
    _name = 'bb.import.lc.details'
    
    # Relationship fields
    bb_import_lc_id = fields.Many2one('bb.import.lc', ondelete="CASCADE")
    
    po_related = fields.Many2one('buyer.work.order', string="PO's to Relate", required=True,
                               domain=[('state', '=', 'confirm')])
    tagged_po = fields.Many2one('buyer.work.order', string="Tagged PO", required=True,
                               domain=[('state', '=', 'confirm')])
    
    
    
    # All function which process data and operation
    
    
    



     
    
    


        
        
            
    
