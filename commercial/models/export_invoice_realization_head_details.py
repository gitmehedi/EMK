from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator


class ExportInvoiceRealizationHeadDetails(models.Model):
    _name = 'export.invoice.realization.head.details'
    
    fc_value = fields.Integer(string="FC Value", required=True)
    lc_value = fields.Integer(string="LC Value", required=True)
    exchange_rate = fields.Integer(string="Exchange Rate", required=True)
    
    # Relationship fields
    export_invoice_distribution_id = fields.Many2one('export.invoice.realization', delegate=True, ondelete='cascade')
    export_invoice_deduction_id = fields.Many2one('export.invoice.realization', delegate=True, ondelete='cascade')
    export_invoice_charge_id = fields.Many2one('export.invoice.realization', delegate=True, ondelete='cascade')
    
    account_id = fields.Many2one('export.invoice', string="Account", required=True,
                               domain=[('state', '=', 'confirm')])
    
    
    # All function which process data and operation
    @api.multi
    def _validate_data(self, value):
        msg , filterNum = {}, {}
        
        filterNum['FC Value'] = value.get('fc_value', False)
        filterNum['LC Value'] = value.get('lc_value', False)
        filterNum['Exchange Rate'] = value.get('exchange_rate', False)
        
        msg.update(validator._validate_number(filterNum))
        validator.validation_msg(msg)
        
        return True
    
    @api.model
    def create(self, vals):
        self._validate_data(vals)
            
        return super(ExportInvoiceRealizationHeadDetails, self).create(vals)
    
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        
        return super(ExportInvoiceRealizationHeadDetails, self).write(vals)   



     
    
    


        
        
            
    
