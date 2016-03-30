from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator


class ImportPaymentHeadDetails(models.Model):
    _name = 'import.payment.head.details'
    
    fc_value = fields.Integer(string="FC Value", required=True)
    lc_value = fields.Integer(string="LC Value", required=True)
    exchange_rate = fields.Integer(string="Exchange Rate", required=True)
    
    # Relationship fields
    import_payment_head_id = fields.Many2one('import.payment', ondelete="CASCADE")
    import_charge_head_id = fields.Many2one('import.payment', ondelete="CASCADE")
    
    
    account_id = fields.Many2one('export.invoice', string="Account", required=True,
                               domain=[('state', '=', 'confirm')])
    
    
    # All function which process data and operation
    @api.multi
    def _validate_data(self, value):
        msg , filterInt = {}, {}
        
        filterInt['FC Value'] = value.get('fc_value', False)
        filterInt['LC Value'] = value.get('lc_value', False)
        filterInt['Exchange Rate'] = value.get('exchange_rate', False)
        
        msg.update(validator._validate_number(filterInt))
        validator.validation_msg(msg)
        
        return True
    
    @api.model
    def create(self, vals):
        self._validate_data(vals)
            
        return super(TTPaymentHeadDetails, self).create(vals)
    
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        
        return super(TTPaymentHeadDetails, self).write(vals)   



     
    
    


        
        
            
    
