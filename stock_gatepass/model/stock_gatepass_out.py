from openerp import api, exceptions, fields, models
from openerp.addons.helper import validator
import datetime
from openerp import _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class StockGatePassOut(models.Model):
    _name = "stock.gatepass.out"
    _description = 'Gate Pass Out'
    
    gete_pass_no = fields.Char("Gate Pass Out Number", readonly=True, copy=False)
    gate_pass_out_code = fields.Char(string='Code')
    date = fields.Datetime('Date',default=datetime.datetime.now(),readonly=True, states={'draft': [('readonly', False)]})
    store_location = fields.Many2one('stock.location', string='Store Location', required=True,
                                      readonly=True, states={'draft': [('readonly', False)]}, domain=[('usage', '=', 'internal')])
    destination_location = fields.Many2one('stock.location', string='Destination Location', readonly=True, states={'draft': [('readonly', False)]}) 
    purpose = fields.Many2one("gatepass.purpose",string="Purpose", required = True, readonly=True, states={'draft': [('readonly', False)]})
    receiving_auth = fields.Many2one('res.users', string="Authority", required=True, readonly=True, states={'draft': [('readonly', False)]})
    gete_pass_type = fields.Many2one('gatepass.type', string="Type", required=True, readonly=True, states={'draft': [('readonly', False)]})
    chalan_no = fields.Char(string="Chalan No", required=True, readonly=True, states={'draft': [('readonly', False)]})
    security_id = fields.Many2one('hr.employee', string="Security Guard", required=True,
                                   readonly=True, states={'draft': [('readonly', False)]}, domain=[('security_guard', '=', True)])
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),('cancel', 'Cancel')], default="draft", readonly=True, states={'draft':[('readonly', False)]})
    gate_pass_out_lines = fields.One2many('stock.gatepass.out.line', 'stock_gatepass_out_id', string='Products', readonly=True, states={'draft': [('readonly', False)]})
    notes = fields.Text("Notes")
    _rec_name = 'gete_pass_no'
    
    @api.one
    @api.constrains('destination_location', 'store_location')
    def _check_location_duplicate(self):
        if self.destination_location and self.store_location and self.destination_location == self.store_location:
            raise exceptions.ValidationError("The store location and destination location can not be same.")

    
    @api.one
    def action_confirm(self):
        self.state = 'confirm'
        res = {}
        new_seq = self.env['ir.sequence'].get('gate_pass_out_code')
        if new_seq:
            res['gete_pass_no'] = new_seq
        self.write(res)
    
    @api.one
    def action_cancel(self):
        self.state = 'cancel'
        
    @api.multi
    def unlink(self):
        for line in self:
            if line.state != "draft":
                raise Warning(_('It can not be deleted'))
            else:
                return super(StockGatePassOut, self).unlink()
    
class StockGatePassOutLine(models.Model):
    _name = "stock.gatepass.out.line"
    _description = 'Gate Pass Out Line'
    
    description = fields.Char("Description", required = True)
    remarks = fields.Text("Remarks")
    product_qty  = fields.Float(digits=(20, 2),string="Quantity", required=True)
    product_qom = fields.Many2one('product.uom', 'Unit of Measure', required=True)
    stock_gatepass_out_id = fields.Many2one('stock.gatepass.out', string="Stock Gate pass Out")
    
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
        return super(StockGatePassOutLine, self).create(vals)
   
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        return super(StockGatePassOutLine, self).write(vals)

    
            