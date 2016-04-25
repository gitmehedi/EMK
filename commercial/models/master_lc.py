from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator
from datetime import date


class MasterLC(models.Model):
    """ Master LC sends sales coantract as a confirmaiton of the export order. 
    Merchandiser receives the sales contract and takes necessary steps """
    
    _name = 'master.lc'
    
    """ Buyer Work Order fields """
    name = fields.Char(string="Serial", size=30, readonly=True)
    mlc_code = fields.Char(string='Code')
    
    lc_no = fields.Char(string="LC No", size=30, required=True)
    
    lc_open_date = fields.Date(string="LC Opening Date", default=date.today().strftime('%Y-%m-%d'), required=True)
    lc_lien_date = fields.Date(string="LC Lien Date", default=date.today().strftime('%Y-%m-%d'))
    lc_expiry_date = fields.Date(string="LC Expiry Date", default=date.today().strftime('%Y-%m-%d'))
    
    lc_value = fields.Float(string="LC Value", digits=(15, 2), required=True)
    tolerance = fields.Float(string='Tolerance (%)', digits=(15, 2))
    inco_term_place = fields.Char(string="Inco Term Place", size=30)
    bb_lc = fields.Integer(string="BB LC Limit", default=False)
    
    remarks = fields.Text(string='Remarks')
    
    """ Relationship fields """
    buyer_id = fields.Many2one('res.partner', string="Buyer", required=True,
                               domain=[('customer', '=', 'True')])
   
    lc_open_bank_id = fields.Many2one('res.bank', string="LC Opening Bank", required=True)
    lc_lien_bank_id = fields.Many2one('res.bank', string="LC Lien Bank")
    lc_advising_bank_id = fields.Many2one('res.bank', string="Advising Bank")
    receive_user_id = fields.Many2one('res.bank', string="Receive Through")
    currency_id = fields.Many2one('res.currency', string="Currency", required=True)
    
    payment_term_id = fields.Many2one('account.payment.term', string="Payment Terms/Tenor",
                                      readonly=True, states={'draft':[('readonly', False)]})
    inco_term_id = fields.Many2one('stock.incoterms', string="Inco Term")
    
    state = fields.Selection([('draft', "Draft"), ('confirm', "Confirm")], default='draft')
    
    """ One2many relationships """
    master_lc_details_ids = fields.One2many('master.lc.details', 'master_lc_id')
    
    allow_partial_shipment = fields.Boolean(string="Allow Partial Shipment")
    allow_trans_shipment = fields.Boolean(string="Allow Trans Shipment")

    """ All kinds of validation message """
    @api.multi
    def _validate_data(self, value):
        msg , filterInt, filterNum, filterChar = {}, {}, {}, {}
        
        filterInt['Tolerance'] = value.get('tolerance', False)
        filterInt['BB LC Limit'] = value.get('bb_lc', False)
        filterNum['LC Value'] = value.get('lc_value', False)
        filterNum['Tenor'] = value.get('tenor', False)
        filterChar['LC No'] = value.get('lc_no', False)
        
        msg.update(validator._validate_percentage(filterInt))
        msg.update(validator._validate_number(filterNum))
        msg.update(validator._validate_character(filterChar, True))
        validator.validation_msg(msg)
        
        return True
    
    
    """ All function which process data and operation """
    
    @api.model
    def create(self, vals):
        self._validate_data(vals)
        vals['name'] = self.env['ir.sequence'].get('mlc_code')
            
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
        
      



     
    
    


        
        
            
    
