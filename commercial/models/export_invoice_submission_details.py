from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator


class ExportInvoiceSubmissionDetails(models.Model):
    """
    Export Invoice Submission Details creates for buyer
    """
    _name = 'export.invoice.submission.details'
    
    value = fields.Integer(string="Value", required=True)
    
    """ Relationship fields """
    export_invoice_submission_id = fields.Many2one('export.invoice.submission', ondelete="cascade")
    
    invoice_id = fields.Many2one('account.invoice', string="Invoice List", required=True)

    """ All function which process data and operation """
    @api.multi
    def _validate_data(self, value):
        msg , filterNum = {}, {}
        
        filterNum['Value'] = value.get('value', False)
        
        msg.update(validator._validate_number(filterNum))
        validator.validation_msg(msg)
        
        return True

    def nolangu(self):
        return self.export_invoice_submission_id.lc_no_id

    @api.onchange('invoice_id')
    def _onchange_invoice_id(self):
        res = {}
        # self.invoice_id = 0

        if self.export_invoice_submission_id.lc_no_id:
            ai_obj = self.env['account.invoice'].search([('lc_id', '=', self.export_invoice_submission_id.lc_no_id.id)])
            res['domain'] = {
                'invoice_id': [('id', 'in', ai_obj.ids)],
            }

        return res

    
    @api.model
    def create(self, vals):
        self._validate_data(vals)
            
        return super(ExportInvoiceSubmissionDetails, self).create(vals)
    
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        
        return super(ExportInvoiceSubmissionDetails, self).write(vals)



     
    
    


        
        
            
    
