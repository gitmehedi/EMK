from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator
from datetime import date


class BBImportLC(models.Model):
    """ 
    Back to Back LC or Import LC
    """
    _name = 'bb.import.lc'
    
    # Mandatory and Optional Fields
    name = fields.Char(string="Serial", size=30, readonly=True)
    bblc_code = fields.Char(string='Code')
    
    lc_apply_date = fields.Date(string="LC Apply Date", required=True, default=date.today().strftime('%Y-%m-%d'))
    lc_open_date = fields.Date(string="LC Open Date", required=True, default=date.today().strftime('%Y-%m-%d'))
    lc_expiry_date = fields.Date(string="LC Expiry Date", required=True, default=date.today().strftime('%Y-%m-%d'))
    
    lc_value = fields.Char(string="LC Value", size=30)
    exchange_rate = fields.Float(string="Exchange Rate", required=True)
    margin = fields.Float(string='Margin', digits=(15, 2), required=True)
    tenor = fields.Integer(string='Tenor', size=30, required=True)
    export_po_value = fields.Char(string="Export PO Value", size=30)
    inco_term_place = fields.Char(string="Inco Term Place", size=30)
    
    remarks = fields.Text(string='Remarks')
    
    # Relationship fields
    supplier_id = fields.Many2one('res.partner', string="Supplier", required=True,
                               domain=[('supplier', '=', 'True')])
   
    lc_open_bank_id = fields.Many2one('res.bank', string="LC Opening Bank", required=True)
    lc_supplier_bank_id = fields.Many2one('res.bank', string="LC Supplier Bank", required=True)
    payment_term = fields.Selection([("10", "10 Days"), ("15", "15 Days"), ("30", "30 Days")], string='Payment Terms', required=True)
    inco_term = fields.Many2one('commercial.term', string="Inco Term", required=True)
    currency = fields.Many2one('res.bank', string="Currency", required=True)
    lc_type = fields.Many2one('res.bank', string="LC Type", required=True)
    
   
    export_po = fields.Many2one('buyer.work.order', string="Export PO", #required=True,
                               domain=[('state', '=', 'confirm')])
    export_lc_currency = fields.Many2one('res.bank', string="Export PO Currency", required=True)
    
 
    
    
    state = fields.Selection([('draft', "Draft"), ('confirm', "Confirm")], default='draft')
    
    # One2many relationships
    bb_import_lc_details_ids = fields.One2many('bb.import.lc.details', 'bb_import_lc_id')
    allow_partial_shipment = fields.Boolean(string="Allow Partial Shipment")
    allow_trans_shipment = fields.Boolean(string="Allow Trans Shipment")
    lc_close = fields.Boolean(string="LC Close")
    
    
    # All kinds of validation message
    
    # All function which process data and operation
    
    @api.model
    def create(self, vals):
#         self._validate_data(vals)
        vals['name'] = self.env['ir.sequence'].get('bblc_code')
            
        return super(BBImportLC, self).create(vals)
    
    @api.multi
    def write(self, vals):
#         self._validate_data(vals)
        
        return super(BBImportLC, self).write(vals)      
    
    
    @api.multi
    def action_draft(self):
        self.state = 'draft'
        
    @api.multi    
    def action_confirm(self):
        self.state = 'confirm'
        
      



     
    
    


        
        
            
    
