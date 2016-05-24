from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator


class ExportInvoiceSubmissionDetails(models.Model):
    _name = 'export.invoice.submission.details'
    
    value = fields.Integer(string="Value", required=True)
    
    """ Relationship fields """
    export_invoice_submission_id = fields.Many2one('export.invoice.submission', ondelete="cascade")
    
    invoice_id = fields.Many2one('account.invoice', string="Invoice No", required=True,
                               domain=[('state', '=', 'draft')])

    """ All function which process data and operation """
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
            
        return super(ExportInvoiceSubmissionDetails, self).create(vals)
    
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        
        return super(ExportInvoiceSubmissionDetails, self).write(vals)



     
    
    


        
        
            
    
