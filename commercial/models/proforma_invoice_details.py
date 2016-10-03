from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator
from datetime import date


class ProformaInvoiceDetails(models.Model):
    """ 
    Proforma Invoice Details
    """
    _name = 'proforma.invoice.details'
  
    qty = fields.Float(string='Quantity', required=True)
    rate = fields.Float(string='Rate', digits=(15, 2), required=True)
    price = fields.Float(string='Price', digits=(15, 2), required=True)
    tax = fields.Float(string='Tax', digits=(15, 2), required=True)
    sub_total = fields.Float(string='Sub Total', digits=(15, 2), required=True)
    schedule_date = fields.Date(string="Schedule Date", required=True, default=date.today().strftime('%Y-%m-%d'))
    description = fields.Char(string='Description', size=200)
  
    # Relationship fields
    product_id = fields.Many2one('product.product', string="Product", required=True)  
    uom_id = fields.Many2one('product.uom', string="UoM", ondelete='set null', required=True,
                             domain=[('category_id', '=', 'Unit')])
    
    proforma_invoice_id = fields.Many2one('proforma.invoice', ondelete="cascade")
    
    
    
    # All function which process data and operation
    # All kinds of validation message
    @api.multi
    def _validate_data(self, value):
        msg , filterChar, filterNum = {}, {}, {}
        filterNum['Quantity'] = value.get('qty', False)
        filterNum['Rate'] = value.get('rate', False)
        filterNum['Price'] = value.get('price', False)
        filterNum['Tax'] = value.get('tax', False)
        filterNum['Sub Total'] = value.get('sub_total', False)
        
        msg.update(validator._validate_number(filterNum))
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
    
    



     
    
    


        
        
            
    
