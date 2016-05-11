from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator


class ProductStyle(models.Model):
    """
    Product Style models create new styles of a product.
    Style has many attribute including technical specification, sizes
    and images.
    """
    _name = 'product.style'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    """
    required and optional fields
    """ 
    name = fields.Char(size=30, string="Serial No", readonly=True)
    style_code = fields.Char(string='Code')
    style_ref = fields.Char(string="Reference Style", size=30, required=True,
                            readonly=True, states={'draft':[('readonly', False)]})
    remarks = fields.Text(string="Remarks", size=300,
                          readonly=True, states={'draft':[('readonly', False)]})
    
    
    image_ids = fields.One2many('product.style.image', 'style_id', string="Images")
    docs_ids = fields.One2many('product.style.docs', 'doc_id', string="Documents")

    buyer_id = fields.Many2one('res.partner', string="Buyer", required=True, domain=[('customer', '=', 'True')],
                               readonly=True, states={'draft':[('readonly', False)]})  
    season_id = fields.Many2one('res.season', string="Season", required=True,
                                readonly=True, states={'draft':[('readonly', False)]})  
    year_id = fields.Many2one('account.fiscalyear', string="Year", required=True,
                              readonly=True, states={'draft':[('readonly', False)]})
    line_ids = fields.One2many('product.style.line', 'style_id', string="Lines",
                               readonly=True, states={'draft':[('readonly', False)]})
    specification_ids = fields.One2many('product.specification.line', 'style_id', string="Specification",
                                        readonly=True, states={'draft':[('readonly', False)]})
    
    """ Product Revised Style fields """
    version = fields.Integer(string='Version', size=3, default=1, readonly=True)
    visible = fields.Boolean(default=True)
    
    style_id = fields.Many2one('product.style', string="Style No", readonly=True)
    ref_style = fields.Many2one('product.style', string="Reference Style", index=True, readonly=True)
    style_ids = fields.One2many('product.style', 'style_id', string="Styles", readonly=True)

    """ State fields for containing vaious states """
    state = fields.Selection([('draft', "Draft"), ('confirm', "Confirm")], default='draft')


    """All function which process data and operation"""
    
    @api.model
    def create(self, vals):
        version = vals.get('version', 0)
        if (version in [0, 1]):
            vals['name'] = self.env['ir.sequence'].get('style_code')
            
        return super(ProductStyle, self).create(vals)
    
    @api.multi
    @api.depends('name', 'style_ref')
    def name_get(self):
        result = []
        for record in self:
            if record.version == 1:
                version = ''
            else:
                version = ': v- ' + str(record.version)    
            result.append((record.id, '[%s%s] %s' % (record.name, version, record.style_ref)))
        return result
    
    @api.multi
    def copy_style(self, default=None):
        default = dict(default or {})
        if default['create_version']:
            # Set Value for the new record
            default['version'] = self.version + 1
            default['ref_style'] = self.id
            default['name'] = self.name
        else:
            default['style_id'] = ''
            default['version'] = 1
          
        res = super(ProductStyle, self).copy(default)
        
        # Update the current record
        if default['create_version']:
            self.write({'visible':False, 'style_id':res.id})
            for st in self.style_ids:
                st.write({'style_id':res.id})
        return res        
        
    
    # Delete record if it states in draft
    def unlink(self, cr, uid, ids, context=None):
        obj = self.pool['product.style']
        
        for item in self.browse(cr, uid, ids, context=context):
            if item.state != 'draft':
                raise exceptions.ValidationError(validator.msg['delete_style'])
                
            obj.unlink(cr, uid, [line.id for line in item.line_ids], context=context)
        return super(ProductStyle, self).unlink(cr, uid, ids, context=context)
        

    @api.multi
    def action_draft(self):
        self.state = 'draft'
        
    def action_confirm(self, cr, uid, ids, context=None):
        res = self.write(cr, uid, ids, {'state':'confirm'}, context)
        return res
    
    
    



     
    
    


        
        
            
    
