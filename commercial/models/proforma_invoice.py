from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator
from datetime import date


class ProformaInvoice(models.Model):
    """ 
    Proforma Invoice 
    """
    _name = 'proforma.invoice'
    
    # mandatory and optional fields
    name = fields.Char(string="Serial", size=30, readonly=True)
    pi_code = fields.Char(string='Code')
    
    pi_no = fields.Char(string="PI No", size=30, required=True)
    pi_date = fields.Date(string="PI Date", required=True, default=date.today().strftime('%Y-%m-%d'))
    remarks = fields.Text(string='Remarks')
    
    # Relationship fields
    supplier_id = fields.Many2one('res.partner', string="Supplier", required=True,
                               domain=[('supplier', '=', 'True')])
    currency = fields.Many2one('res.bank', string="Currency", required=True)
    delivery_term = fields.Many2one('delivery.term', string="Delivery Term")
    delivery_to = fields.Many2one('res.partner', string="Delivery To")
    
    state = fields.Selection([('draft', "Draft"), ('confirm', "Confirm")], default='draft')
    
    # One2many relationships
    proforma_invoice_details_ids = fields.One2many('proforma.invoice.details', 'proforma_invoice_id')
    
    
    # All kinds of validation message
    @api.multi
    def _validate_data(self, value):
        msg , filterChar = {}, {}
        
        filterChar['PI No'] = value.get('pi_no', False)
        
        msg.update(validator._validate_character(filterChar, True))
        validator.validation_msg(msg)
        
        return True
    
    
    # All function which process data and operation
    
    @api.model
    def create(self, vals):
        self._validate_data(vals)
        vals['name'] = self.env['ir.sequence'].get('pi_code')
            
        return super(MasterLC, self).create(vals)
    
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        
        return super(MasterLC, self).write(vals)      
    
    
    @api.multi
    def action_draft(self):
        self.state = 'draft'
        
    @api.multi    
    def action_confirm(self):
        self.state = 'confirm'
        
      



     
    
    


        
        
            
    
