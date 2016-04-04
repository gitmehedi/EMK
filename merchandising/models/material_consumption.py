from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator


class MaterialConsumption(models.Model):
    """
    Material Consumption
    """
    _name = 'material.consumption'
    
    """Requied and Optional Fields"""
    name = fields.Char(string="Material Consumption", size=50, readonly=True)
    material_seq = fields.Char()
    consumtion_qty = fields.Integer(string='Consumption For', size=11, default=1, required=True,
                                    readonly=True, states={'draft':[('readonly', False)]})
    
    template = fields.Boolean(default=False)
   
    
    """Model Relationship"""
    style_id = fields.Many2one('product.style', string="Style No", required=True,
                               readonly=True, states={'draft':[('readonly', False)]}, domain=[('visible', '=', 'True'), ('state', '=', 'confirm')])
    po_id = fields.Many2one('buyer.work.order', string="Work Order No",
                            readonly=True, states={'draft':[('readonly', False)]},domain=[('state', '=', 'confirm')])
    uom_id = fields.Many2one('product.uom', string="UoM", ondelete='set null', required=True,
                             readonly=True, states={'draft':[('readonly', False)]}, domain=[('category_id', '=', 'Unit')])
    
    """ One2many Relationship"""
    yarn_ids = fields.One2many('material.consumption.details', 'mc_yarn_id', string="Yarn",
                               readonly=True, states={'draft':[('readonly', False)]})
    acc_ids = fields.One2many('material.consumption.details', 'mc_acc_id', string="Accessories",
                              readonly=True, states={'draft':[('readonly', False)]})
    
    """State fields for containing vaious states"""
    state = fields.Selection([('draft', "Draft"), ('confirm', "Confirm")], default='draft')
    
   
    """ All function which process data and operation"""
   
    @api.multi
    def _validate_data(self, value):
        msg , filterInt = {}, {}


        filterInt['Consumption For'] = value.get('consumtion_qty', False)
        if filterInt['Consumption For']:
            msg.update(validator._validate_number(filterInt))
            validator.validation_msg(msg)
        
        return True
    
    
    @api.model
    def create(self, vals):
        self._validate_data(vals)
        vals['name'] = self.env['ir.sequence'].get('material_seq')
        
        return super(MaterialConsumption, self).create(vals)
   
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        return super(MaterialConsumption, self).write(vals)
    
    
    @api.onchange('style_id')
    def _onchange_style_id(self):
        res, ids = {}, []
        self.po_id = 0

        if self.style_id:
            bwo_obj = self.env['buyer.work.order'].search([('style_id','=',self.style_id.id)])
            res['domain'] = {
                    'po_id': [('id', 'in', bwo_obj.ids)],
            }

        return res

    def create_template(self, cr, uid, ids, context=None):
        res = self.write(cr, uid, ids, {'template':True}, context)
        return res
    
    @api.multi
    def action_draft(self):
        self.state = 'draft'
         
    def action_confirm(self, cr, uid, ids, context=None):
        res = self.write(cr, uid, ids, {'state':'confirm'}, context)
        return res
    
    



     
    
    


        
        
            
    
