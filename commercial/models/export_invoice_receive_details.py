from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator


class ExportInvoiceReceiveDetails(models.Model):
    _name = 'export.invoice.receive.details'
    
    value = fields.Integer(string="Value", required=True)
    
    # Relationship fields
    export_invoice_receive_id = fields.Many2one('export.invoice.receive', delegate=True, ondelete="cascade")
    
    invoice_id = fields.Many2one('export.invoice', string="Invoice No", required=True,
                               domain=[('state', '=', 'confirm')])
    
    
    
    
    # All function which process data and operation
    @api.multi
    def _validate_data(self, value):
        msg , filterNum = {}, {}
        
        filterNum['Value'] = value.get('value', False)
        
        msg.update(validator._validate_number(filterNum))
        validator.validation_msg(msg)
        
        return True
    
    @api.model
    def create(self, vals):
        self._validate_data(vals)
            
        return super(ExportInvoiceReceiveDetails, self).create(vals)
    
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        
        return super(ExportInvoiceReceiveDetails, self).write(vals)   



     
    
    


        
        
            
    
