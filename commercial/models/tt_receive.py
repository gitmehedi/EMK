from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator
from datetime import date



class TTReceive(models.Model):
    """ 
    Telegraphic Receive creates for buyer 
    """
    _name = 'tt.receive'
    
    # Mandaroty and Optional Fields
    name = fields.Char(string="Serial", size=30, readonly=True)
    ttr_code = fields.Char(string='Code')
    
    tt_receive_date = fields.Date(string="TT Receive Date", required=True, default=date.today().strftime('%Y-%m-%d'))
    
    remarks = fields.Text(string='Remarks')
    
    # Relational fields
    buyer_id = fields.Many2one('res.partner', string="Buyer", required=True,
                               domain=[('customer', '=', 'True')])
    tt_payment_bank_id = fields.Many2one('res.bank', string="TT Payment Bank", required=True)
    tt_receive_bank_id = fields.Many2one('res.bank', string="TT Receive Bank", required=True)
    currency = fields.Many2one('res.currency', string="Currency", required=True)
    receive_process = fields.Selection([('full_receive', "Full Payment Receive"), ('advance_receive', "Advance Receive")],string="Receive Process")
    
    state = fields.Selection([('draft', "Draft"), ('confirm', "Confirm")], default='draft')
    
    
    # one2many relational fields
    tt_recv_distribution_head_ids = fields.One2many('tt.receive.head.details', 'tt_distribution_head_id')
    tt_recv_deduction_head_ids = fields.One2many('tt.receive.head.details', 'tt_deduction_head_id')
    tt_recv_charge_head_ids = fields.One2many('tt.receive.head.details', 'tt_charge_head_id')
    
    
    # All function which process data and operation
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('ttr_code')
            
        return super(TTReceive, self).create(vals)
    
    @api.multi
    def write(self, vals):
        return super(TTReceive, self).write(vals)      
    
    
    @api.multi
    def action_draft(self):
        self.state = 'draft'
        
    @api.multi    
    def action_confirm(self):
        self.state = 'confirm'
        
      



     
    
    


        
        
            
    
