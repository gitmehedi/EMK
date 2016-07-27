from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator


class BwoShipmentDetails(models.Model):
    _name = 'bwo.shipment.details'
    
    # Buyer Work Order Shipment Fields
    name = fields.Char(string="Shipment Title", size=30, required=True)
    shipment_date = fields.Date(string="Shipment Date", size=30, required=True)
    buyer_inspection_date = fields.Date(string="Buyer Inspection Date", size=30, required=True)
    in_house_inspection_date = fields.Date(string="In House Inspection Date", size=30, required=True)
    
    # Relationship fields
    bwo_details_id = fields.Many2one('sale.order')
    
    # All function which process data and operation
    
    @api.multi
    def _validate_data(self, value):
        msg , filterChar = {}, {}
        
        filterChar['Shipment Title'] = value.get('name', False)
        
        msg.update(validator._validate_character(filterChar, True))
        validator.validation_msg(msg)
        
        return True
    
    
    @api.model
    def create(self, vals):
        self._validate_data(vals)
        vals['name'] = vals.get('name', False).strip()
        return super(BwoShipmentDetails, self).create(vals)    
    
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        
        if vals['name']:
            vals['name'] = vals.get('name', False).strip()
        
        return super(BwoShipmentDetails, self).write(vals)  
    




     
    
    


        
        
            
    
