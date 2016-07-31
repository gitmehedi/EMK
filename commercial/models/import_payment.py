from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator
from datetime import date



class ImportPayment(models.Model):
    """ Import Payment creates for buyer """
    
    _name = 'import.payment'
    
    # Buyer Work Order fields
    name = fields.Char(string="Serial", size=30, readonly=True)
    ip_code = fields.Char(string='Code')
    
    invoice_no = fields.Char(string="Invoice No", size=30)
    import_payment_date = fields.Date(string="Payment Date", required=True, default=date.today().strftime('%Y-%m-%d'))
    acceptance_value = fields.Char(string="Acceptance Value", size=30)
    
    remarks = fields.Text(string='Remarks')
    
    # Relational fields
    import_payment_bank_id = fields.Many2one('res.bank', string="TT Payment Bank", required=True)
    
    
    state = fields.Selection([('draft', "Draft"), ('confirm', "Confirm")], default='draft')
    
    # one2many relational fields
    import_pay_payment_head_ids = fields.One2many('import.payment.head.details', 'import_payment_head_id')
    import_pay_charge_head_ids = fields.One2many('import.payment.head.details', 'import_charge_head_id')
    
    
    # All function which process data and operation
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('ip_code')
            
        return super(ImportPayment, self).create(vals)
    
    @api.multi
    def write(self, vals):
        return super(ImportPayment, self).write(vals)      
    
    
    @api.multi
    def action_draft(self):
        self.state = 'draft'
        
    @api.multi    
    def action_confirm(self):
        self.state = 'confirm'
        
      



     
    
    


        
        
            
    
