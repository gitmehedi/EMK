from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator
from datetime import date


class ExportInvoiceReceive(models.Model):
    """ 
    Export Invoice Receive creates for buyer 
    """
    
    _name = 'export.invoice.receive'
    
    # Buyer Work Order fields
    name = fields.Char(string="Serial", size=30, readonly=True)
    eir_code = fields.Char(string='Code')
    
    submission_date = fields.Date(string="Submission Date", required=True, default=date.today().strftime('%Y-%m-%d'))
    bank_ref_no = fields.Char(string="Bank Ref No", size=30, required=True)
    submission_type = fields.Selection([('submission', 'Submission'), ('negotiation', 'Negotiation')],
                                       string="Submission Type", required=True)
    realization_date = fields.Date(string="Realization Date", required=True, default=date.today().strftime('%Y-%m-%d'))
    
    
    remarks = fields.Text(string='Remarks')
    
    # Relational fields
    currency = fields.Many2one('res.currency', string="Currency", required=True)
    state = fields.Selection([('draft', "Draft"), ('confirm', "Confirm")], default='draft')
    
    # one2many relational fields
    invoice_receive_details_ids = fields.One2many('export.invoice.receive.details', 'export_invoice_receive_id')
    invoice_receive_negotiation_ids = fields.One2many('export.invoice.receive.negotiation', 'export_invoice_receive_id')
    
    # All kinds of validation message
    def _validate_data(self, vals):
        msg, filterChar = {}, {}
        
        filterChar['bank_ref_no'] = value.get('bank_ref_no', False)
        
        msg.update(validator._validate_character(filterChar, True))
        validator.validation_msg(msg)
    # All function which process data and operation
    
    @api.model
    def create(self, vals):
        self._validate_data(vals)
        vals['name'] = self.env['ir.sequence'].get('eir_code')
            
        return super(ExportInvoiceReceive, self).create(vals)
    
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        
        return super(ExportInvoiceReceive, self).write(vals)      
    
    
    @api.multi
    def action_draft(self):
        self.state = 'draft'
        
    @api.multi    
    def action_confirm(self):
        self.state = 'confirm'
        
      



     
    
    


        
        
            
    
