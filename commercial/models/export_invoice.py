from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator
from datetime import date


class ExportInvoice(models.Model):
    """ 
    Inherit Account Invoice master model and names as Export Invoice
    """
    _inherit = 'account.invoice'


    """ Export invoice fields """
    name = fields.Char(string="Serial", size=30, readonly=True)
    ei_code = fields.Char(string='Code')
    
    invoice_against = fields.Selection([('lc', 'LC'), ('tt', 'TT')], string="Invoice Against", required=True) 
    lc_tt_no = fields.Char(string="Export LC/TT No", size=30, required=True)
    ei_date = fields.Date(string="Export Invoice Date", required=True, default=date.today().strftime('%Y-%m-%d'))
    
    
    destination = fields.Char(string="Destination", size=30, required=True)
    mother_vessel = fields.Char(string="Mother Vessel", size=30, required=True)
    feader_vessel = fields.Char(string="Feader Vessel", size=30, required=True)
    shipping_mark = fields.Char(string="Shipping Mark", size=30, required=True)
    no_of_container = fields.Integer(string="No of Container")
    eta = fields.Char(string="ETA", size=30, required=True)
    invoice_value = fields.Char(string="Invoice Value", size=30, required=True)
    discount = fields.Char(string="Discount %", size=30, required=True)
    discount_amount = fields.Char(string="Discount Amount", size=30, required=True)
    net_invoice_value = fields.Char(string="Net Invoice Value", size=30, required=True)
   
    conversion_rate = fields.Integer(string="Conversion Rate", required=True)
    invoice_value_bdt = fields.Integer(string="Invoice Value (BDT)", required=True)
    buying_house_com = fields.Integer(string="Buying House Com", required=True)
    
    
    remarks = fields.Text(string='Remarks')
    
    """ Relational fields """
    export_invoice_id = fields.Many2one('res.bank', string='Export Invoice No', required=True)
    consignee = fields.Many2one('res.bank', string='Consignee', required=True)
    notify_party = fields.Many2one('res.partner', string='Notify Party', required=True)
    port_of_loading = fields.Many2one('port', string='Port of Loading', required=True)
    port_of_discharge = fields.Many2one('port', string='Port of Discharge', required=True)
    currency = fields.Many2one('res.currency', string="Currency", required=True)
    payment_term_id = fields.Many2one('account.payment.term', string="Payment Terms/Tenor",
                                      readonly=True, states={'draft':[('readonly', False)]})
    inco_term_id = fields.Many2one('stock.incoterms', string="Inco Term",
                                   readonly=True, states={'draft':[('readonly', False)]})
    
    # One2many relationships
    shipment_mode = fields.Selection([("sea", "Sea"), ("air", "Air"), ("road", "By Road")], string='Ship Mode',
                                     readonly=True, states={'draft':[('readonly', False)]})
    state = fields.Selection([('draft', "Draft"), ('confirm', "Confirm")], default='draft')
    
    # All kinds of validation message
    @api.multi
    def _validate_data(self, value):
        msg , filterInt, filterNum, filterChar = {}, {}, {}, {}
        
        filterChar['Export LC/TT No'] = value.get('lc_tt_no', False)
        filterInt['Discount'] = value.get('discount', False)
        filterNum['No of Container'] = value.get('no_of_container', False)
        filterNum['Invoice Value'] = value.get('invoice_value', False)
        filterNum['Discount Amount'] = value.get('discount_amount', False)
        filterNum['Net Invoice Value'] = value.get('net_invoice_value', False)
        filterNum['Conversion Rate'] = value.get('conversion_rate', False)
        filterNum['Invoice Value (BDT)'] = value.get('invoice_value_bdt', False)
        filterNum['Buying House Com'] = value.get('buying_house_com', False)
        
        
        msg.update(validator._validate_percentage(filterInt))
        msg.update(validator._validate_number(filterNum))
        msg.update(validator._validate_character(filterChar, True))
        validator.validation_msg(msg)
        
        return True
    
    
    # All function which process data and operation
    
    @api.model
    def create(self, vals):
        self._validate_data(vals)
        vals['name'] = self.env['ir.sequence'].get('ei_code')
            
        return super(ExportInvoice, self).create(vals)
    
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        
        return super(ExportInvoice, self).write(vals)      
    
    
    @api.multi
    def action_draft(self):
        self.state = 'draft'
        
    @api.multi    
    def action_confirm(self):
        self.state = 'confirm'

