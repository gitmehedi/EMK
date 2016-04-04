from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator
from datetime import date



class TTPayment(models.Model):
    """ Telegraphic Payment creates for buyer """
    
    _name = 'tt.payment'
    
    # Buyer Work Order fields
    name = fields.Char(string="Serial", size=30, readonly=True)
    ttp_code = fields.Char(string='Code')
    
    tt_payment_date = fields.Date(string="TT Payment Date", required=True, default=date.today().strftime('%Y-%m-%d'))
    
    remarks = fields.Text(string='Remarks')
    
    # Relational fields
    supplier_id = fields.Many2one('res.partner', string="Supplier", required=True,
                               domain=[('supplier', '=', 'True')])
    tt_payment_bank_id = fields.Many2one('res.bank', string="TT Payment Bank", required=True)
    supplier_bank_id = fields.Many2one('res.bank', string="Supplier Bank", required=True)
    currency = fields.Many2one('res.bank', string="Currency", required=True)
    
    
    state = fields.Selection([('draft', "Draft"), ('confirm', "Confirm")], default='draft')
    
    # one2many relational fields
    tt_pay_payment_head_ids = fields.One2many('tt.payment.head.details', 'tt_payment_head_id')
    tt_pay_charge_head_ids = fields.One2many('tt.payment.head.details', 'tt_charge_head_id')
    
    
    # All function which process data and operation
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('ttr_code')
            
        return super(TTPayment, self).create(vals)
    
    @api.multi
    def write(self, vals):
        return super(TTPayment, self).write(vals)      
    
    
    @api.multi
    def action_draft(self):
        self.state = 'draft'
        
    @api.multi    
    def action_confirm(self):
        self.state = 'confirm'
        
      



     
    
    


        
        
            
    
