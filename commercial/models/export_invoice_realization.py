from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator
from datetime import date


class ExportInvoiceRealization(models.Model):
    """ 
    Export Invoice Realization creates for buyer 
    """
    _name = 'export.invoice.realization'
    
    # Buyer Work Order fields
    name = fields.Char(string="Serial", size=30, readonly=True)
    eirel_code = fields.Char(string='Code')
    
    bank_ref_no = fields.Char(string="Bank Ref No", size=30, required=True)
    realization_date = fields.Date(string="Submission Date", required=True, default=date.today().strftime('%Y-%m-%d'))
    invoice_value = fields.Integer(string="Invoice Value", required=True)
    remarks = fields.Text(string='Remarks')
    
    state = fields.Selection([('draft', "Draft"), ('confirm', "Confirm")], default='draft')
    
    # one2many relational fields
    inv_real_distribution_head_ids = fields.One2many('export.invoice.realization.head.details', 'export_invoice_distribution_id')
    inv_real_deduction_head_ids = fields.One2many('export.invoice.realization.head.details', 'export_invoice_deduction_id')
    inv_real_charge_head_ids = fields.One2many('export.invoice.realization.head.details', 'export_invoice_charge_id')
    
    
    # All function which process data and operation
    @api.multi
    def _validate_data(self, value):
        msg , filterNum, filterChar = {}, {}, {}
        
        filterChar['Bank Ref No'] = value.get('bank_ref_no', False)
        filterNum['Invoice Value'] = value.get('invoice_value', False)
        
        msg.update(validator._validate_character(filterChar, True))
        msg.update(validator._validate_number(filterNum))
        validator.validation_msg(msg)
        
        return True
    
    @api.model
    def create(self, vals):
        self._validate_data(vals)
        vals['name'] = self.env['ir.sequence'].get('eirel_code')
            
        return super(ExportInvoiceRealization, self).create(vals)
    
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        
        return super(ExportInvoiceRealization, self).write(vals)      
    
    
    @api.multi
    def action_draft(self):
        self.state = 'draft'
        
    @api.multi    
    def action_confirm(self):
        self.state = 'confirm'
        
      



     
    
    


        
        
            
    
