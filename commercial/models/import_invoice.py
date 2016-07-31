from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator
from datetime import date


class ImportInvoice(models.Model):
    """ Import Invoice creates for buyer """
    
    _name = 'import.invoice'
    
    # Buyer Work Order fields
    name = fields.Char(string="Serial", size=30, readonly=True)
    ii_code = fields.Char(string='Code')
    
    
    lc_tt_no = fields.Char(string="Import LC/TT No", size=30, required=True)
    ii_date = fields.Date(string="Import Invoice Date", required=True, default=date.today().strftime('%Y-%m-%d'))
    
    
    destination = fields.Char(string="Destination", size=30, required=True)
    eta = fields.Char(string="ETA", size=30, required=True)
    import_invoice_value = fields.Char(string="Import Invoice Value", size=30, required=True)
    invoice_value_bdt = fields.Char(string="Invoice Value (BDT)", size=30, required=True)
    
    
    remarks = fields.Text(string='Remarks')
    
    # Relational fields
    invoice_against = fields.Many2one('res.bank', string="Invoice Against", required=True) 
    import_invoice_id = fields.Many2one('res.bank', string='Import Invoice No', required=True)
    consignee = fields.Many2one('res.bank', string='Consignee', required=True)
    port_of_loading = fields.Many2one('res.bank', string='Port of Loading', required=True)
    port_of_discharge = fields.Many2one('res.bank', string='Port of Discharge', required=True)
    currency = fields.Many2one('res.bank', string="Currency", required=True)
    
    # One2many relationships
    
    
    state = fields.Selection([('draft', "Draft"), ('confirm', "Confirm")], default='draft')
    
    # All kinds of validation message
    @api.multi
    def _validate_data(self, value):
        msg , filterInt, filterNum, filterChar = {}, {}, {}, {}
        
        filterInt['Tolerance'] = value.get('tolerance', False)
        filterInt['Delay'] = value.get('delay', False)
        filterNum['Production Quantity'] = value.get('production_qty', False)
        filterChar['Hs Code'] = value.get('hs_code', False)
        
        msg.update(validator._validate_percentage(filterInt))
        msg.update(validator._validate_number(filterNum))
        msg.update(validator._validate_character(filterChar, True))
        validator.validation_msg(msg)
        
        return True
    
    
    # All function which process data and operation
    
    @api.model
    def create(self, vals):
#         self._validate_data(vals)
        vals['name'] = self.env['ir.sequence'].get('sc_code')
            
        return super(ExportInvoice, self).create(vals)
    
    @api.multi
    def write(self, vals):
#         self._validate_data(vals)
        
        return super(ExportInvoice, self).write(vals)      
    
    
    @api.multi
    def action_draft(self):
        self.state = 'draft'
        
    @api.multi    
    def action_confirm(self):
        self.state = 'confirm'

