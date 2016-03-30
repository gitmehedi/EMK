from openerp import api, exceptions, fields, models
from openerp.addons.helper import validator
import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp import _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class StockGatePassIn(models.Model):
    _name = "stock.gatepass.in"
    _description = 'Gate Pass In'
    
    gete_pass_no = fields.Char("Gate Pass In Number", readonly=True, copy=False)
    gate_pass_in_code = fields.Char(string='Code')
    date = fields.Datetime('Date',default=datetime.datetime.now(),readonly=True, states={'draft': [('readonly', False)]})
    store_location = fields.Many2one('stock.location', string='Store Location', required=True, 
                                     readonly=True, states={'draft': [('readonly', False)]}, domain=[('usage', '=', 'internal')])
    source_location = fields.Many2one('stock.location', string='From Location', readonly=True, states={'draft': [('readonly', False)]}) 
    purpose = fields.Many2one("gatepass.purpose",string="Purpose", required = True, readonly=True, states={'draft': [('readonly', False)]})
    sending_auth = fields.Many2one('res.partner', string="Sending Authority", required=True, readonly=True, states={'draft': [('readonly', False)]})
    receiving_auth = fields.Many2one('res.users', string="Receiving Authority", required=True, readonly=True, states={'draft': [('readonly', False)]})
    gete_pass_type = fields.Many2one('gatepass.type', string="Type", required=True, readonly=True, states={'draft': [('readonly', False)]})
    chalan_no = fields.Char(string="Chalan No", required=True, readonly=True, states={'draft': [('readonly', False)]})
    get_pass_out_no = fields.Many2one('stock.gatepass.out', string="Stock Gate pass Out", readonly=True, states={'draft': [('readonly', False)]})
    security_id = fields.Many2one('hr.employee', string="Security Guard", required=True,
                                   readonly=True, states={'draft': [('readonly', False)]}, domain=[('security_guard', '=', True)])
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('cancel', 'Cancel')], default="draft", readonly=True, states={'draft':[('readonly', False)]})
    gate_pass_in_lines = fields.One2many('stock.gatepass.in.line', 'stock_gatepass_in_id', string='Products', readonly=True, states={'draft': [('readonly', False)]})
    notes = fields.Text("Notes")
    _rec_name = 'gete_pass_no'
    
    @api.one
    def action_confirm(self):
        self.state = 'confirm'
        res = {}
        new_seq = self.env['ir.sequence'].get('gate_pass_in_code')
        if new_seq:
            res['gete_pass_no'] = new_seq
        self.write(res)
    
    @api.multi
    def unlink(self):
        if self.state == "confirm":
            raise Warning(_('It can not be deleted'))
        else:
            return super(StockGatePassIn, self).unlink()
            

class GatePassType(models.Model):
    _name = 'gatepass.type'
    _description = 'Gate Pass Type'

    name= fields.Char('Name', size=256, required=True)
    active= fields.Boolean('Active')

    _defaults = {
        'active': True,
        'return_type': 'return'
    }

class GatePassPurpose(models.Model):
    _name = 'gatepass.purpose'
    _description = 'Gate Pass Purpose'

    name= fields.Char('Name', size=256, select=1)
    active= fields.Boolean('Active')

    _defaults = {
        'active': True
    }
    
class StockGatePassInLine(models.Model):
    _name = "stock.gatepass.in.line"
    _description = 'Gate Pass In Line'
    
    description = fields.Char("Description", required = True)
    remarks = fields.Text("Remarks")
    product_qty  = fields.Float(digits=(20, 2),string="Quantity", required=True)
    product_qom = fields.Many2one('product.uom', 'Unit of Measure', required=True)
    stock_gatepass_in_id = fields.Many2one('stock.gatepass.in', string="Stock Gate pass In")
    
    @api.multi
    def _validate_data(self, value):
        msg , filterInt = {}, {}
        
        filterInt['Quantity'] = value.get('product_qty', False)
       
        msg.update(validator._validate_number(filterInt))
        validator.validation_msg(msg)
        
        return True
            

        
    @api.model
    def create(self, vals):
        self._validate_data(vals)
        return super(StockGatePassInLine, self).create(vals)
   
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        return super(StockGatePassInLine, self).write(vals)
    
    
            