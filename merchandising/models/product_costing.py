from openerp import api, fields, models
from openerp.addons.helper import validator, utility
from openerp.osv import osv
import re
import copy


class ProductCosting(models.Model):
    """
    Product Costing
    """
    _name = "product.costing"

    name = fields.Char(string="Style", size=30, readonly=True)
    procos_code = fields.Char(string='Code')
    buyer_ref = fields.Char(string="Reference", size=30, required=True,
                             readonly=True, states={'draft':[('readonly', False)]})
    
    version = fields.Integer(string="Version", required=True, size=3, default=1, readonly=True)
    version_date = fields.Date(string='Version Date', default=fields.Date.today,
                                    size=30, required=True, readonly=True, states={'draft':[('readonly', False)]})

    qty = fields.Float(string='Quantity', digits=(20, 2),
                       readonly=True, states={'draft':[('readonly', False)]})
    product_costing_visible = fields.Boolean(default=True)
    for_bidding = fields.Boolean(string="Bid", default=True,
                                 readonly=True, states={'draft':[('readonly', False)]})
    weight_per_pcs = fields.Float(string="Weight", required=True,
                                  readonly=True, states={'draft':[('readonly', False)]})
    weight_per_dzn = fields.Float(compute="_compute_weight_per_dzn", required=True, store=True,copy=True,
                                  readonly=True, states={'draft':[('readonly', False)]})
    remarks = fields.Text(string="Remarks", size=300,
                          readonly=True, states={'draft':[('readonly', False)]})
    
    """
    Refactor this fields if noting necessary
    """
    yarn_amount_flag = fields.Boolean(default=False)
    accessories_amount_flag = fields.Boolean(default=False)
    cm_amount_flag = fields.Boolean(default=False) 
    product_current_rate = fields.Float(string='Current Rate', digits=(20, 4))
    product_converted_rate = fields.Float(string='Product Convert Rate', digits=(20, 6))
            
     
    """ 
    Many2one Relational Fields
    """
    buyer_id = fields.Many2one('res.partner', string="Buyer", required=True, domain=[('customer', '=', 'True')],
                               readonly=True, states={'draft':[('readonly', False)]})
    dept_id = fields.Many2one('merchandising.dept', string="Department",
                              readonly=True, states={'draft':[('readonly', False)]})
    uom = fields.Many2one('product.uom', string="UOM", ondelete='set null', domain=[('category_id', '=', 'Unit')]
                          , readonly=True, states={'draft':[('readonly', False)]})
    weight_uom = fields.Many2one('product.uom', ondelete='set null', required=True,
                                 domain=[('category_id', '=', 'Weight')], default=lambda self: self._get_default_uom('lb(s)'),
                                 readonly=True, states={'draft':[('readonly', False)]})
    weight_type = fields.Selection([ ('dzn', 'Dzn'), ('pcs', 'Pcs')], default='dzn', required=True, store=True,
                                       readonly=True, states={'draft':[('readonly', False)]})
    product_currency_id = fields.Many2one('res.currency', string="Currency", required=True,
           readonly=True, states={'draft':[('readonly', False)]}, default=lambda self: self._get_default_currency('USD'))
    product_size_group_id = fields.Many2one('product.size.group', string="Size Group", ondelete='set null'
                                            , readonly=True, states={'draft':[('readonly', False)]})
    style_id = fields.Many2one('product.style', string="Style",
                               domain=[('visible', '=', 'True'), ('state', '=', 'confirm')],
                               readonly=True, states={'draft':[('readonly', False)]})
    gauge_id = fields.Many2one('product.gauge', string="Gauge",
                               readonly=True, states={'draft':[('readonly', False)]})
    costing_id = fields.Many2one('product.costing', string="Costing", readonly=True)
    ref_costing_id = fields.Many2one('product.costing', string="Reference Costing", index=True, readonly=True)
    quotation_type = fields.Selection([('prequote', 'Pre-Quote'), ('finalquote', 'Final-Quote')], 'Quotation Type',
                                       readonly=True, states={'draft':[('readonly', False)]})
    yarn_sum_percentage = fields.Float(compute="_compute_yarn_sum_percentage", digits=(20, 4), store=True)
    
    """ 
    One2many Relational Fields
    """
    yarn_ids = fields.One2many('product.costing.line', 'yarn_costing_id', string="Yarn",
                                readonly=True, states={'draft':[('readonly', False)]}, copy=True)
    accessories_ids = fields.One2many('product.costing.accessories', 'accessories_costing_id', string="Accessories",
                                       readonly=True, states={'draft':[('readonly', False)]}, copy=True)
    cm_ids = fields.One2many('cm.costing.line', 'cm_costing_id', string="CM",
                                readonly=True, states={'draft':[('readonly', False)]}, copy=True)
    costing_ids = fields.One2many('product.costing', 'costing_id', string="Costing", readonly=True)
    
    
    """
    Summary Computed Fields
    """
    total_yarn_cost = fields.Float(compute="_compute_yarn_cost", string='Yarn/Dzn',
                                    digits=(20, 4), default=0.0, store=True, copy=True)
    linking_yarn_cost = fields.Float(string='Linking Yarn/Dzn', digits=(20, 4), default=0.0, store=True, copy=True,
                                     readonly=True, states={'draft':[('readonly', False)]})
    total_accessories_cost = fields.Float(compute="_compute_total_accessories_cost", string='Accessories/Dzn',
                                          digits=(20, 4), default=0.0, store=True, copy=True)
    fabric_cost = fields.Float(string='Fabric/Dzn', digits=(20, 4), default=0.0, store=True, copy=True,
                               readonly=True, states={'draft':[('readonly', False)]})
    embrodery_cost = fields.Float(string='Embrodery/Dzn', digits=(20, 4), default=0.0, store=True, copy=True,
                                  readonly=True, states={'draft':[('readonly', False)]})
    print_cost = fields.Float(string='Print/Dzn', digits=(20, 4), default=0.0, store=True, copy=True,
                              readonly=True, states={'draft':[('readonly', False)]})
    lab_test_cost = fields.Float(string='Lab Test/Dzn', digits=(20, 4), default=0.0, store=True, copy=True,
                                 readonly=True, states={'draft':[('readonly', False)]})
    total_cm_cost = fields.Float(compute="_compute_cm_costs", string='Total CM Cost', digits=(20, 4),
                                 default=0.0, store=True, copy=True)
    total_summary_cost = fields.Float(compute="_compute_total_summary_cost", string='Total Cost',
                                      digits=(20, 4), default=0.0, store=True, copy=True)
    
    commercial_cost = fields.Float(compute='_compute_commercial_cost', string='Commercial Cost/Dzn',
                                   digits=(20, 4), default=0.0, store=True, copy=True)
    commercial_cost_percentage = fields.Float(string='Percentage', digits=(20, 2), default=0.0,
                                              readonly=True, states={'draft':[('readonly', False)]})
    profit = fields.Float(compute='_compute_proifit', string='Profit', digits=(20, 4), default=0.0, store=True, copy=True)
    profit_percentage = fields.Float(string='Profit Percentage', digits=(20, 2), default=0.0,
                                     readonly=True, states={'draft':[('readonly', False)]})
    total_head_commission = fields.Float(compute="_compute_total_head_commission", string='Total Cost',
                                         digits=(20, 4), default=0.0, store=True)
    
    buying_house_commission = fields.Float(compute="_compute_buying_house_commission", string='Buying House Commission',
                                           digits=(20, 4), default=0.0, store=True)
    buying_house_percentage = fields.Float(string='Profit Percentage', digits=(20, 2), default=0.0,
                                           readonly=True, states={'draft':[('readonly', False)]})
    grand_total = fields.Float(compute="_computed_grand_total", string='Grand Total/Dzn', digits=(20, 4), default=0.0, store=True)
    fob_cost = fields.Float(compute="_computed_fob_cost", string='Cost Per Piece (FOB)', digits=(20, 4), default=0.0, store=True)
    
    """
    CM Calculation Fieldsstore=True,
    """
    fixed_overhead_currency_id = fields.Many2one('res.currency', readonly=True, states={'draft':[('readonly', False)]})
    fixed_overhead_bonus_percentage = fields.Float(digits=(20, 4), default=0.0,
                                                   readonly=True, states={'draft':[('readonly', False)]})
    
    fixed_overhead_cm_cost_usd = fields.Float(compute="_compute_fixed_overhead_cm_cost_usd", string="Fixed Overhead Cost on Service (%)", digits=(20, 4), default=0.0, store=True, copy=True)
    fixed_overhead_cm_cost_bdt = fields.Float(compute="_compute_fixed_overhead_cm_cost_bdt", digits=(20, 4), default=0.0, store=True, copy=True)
    
    total_cm_cost_usd = fields.Float(compute="_compute_total_cm_cost_usd", string="Total CM", digits=(20, 4), default=0.0, store=True, copy=True)
    total_cm_cost_bdt = fields.Float(compute="_compute_total_cm_cost_bdt", digits=(20, 4), default=0.0, store=True, copy=True)
    
    """
    States and Constraints
    """
    state = fields.Selection([('draft', "Draft"), ('confirm', "Confirm"), ('approve', "Approve"), ('revise', "Revise"),
                              ('reject', "Reject"), ('cancel', "Cancel")], default='draft',
                             readonly=True, states={'draft':[('readonly', False)]})

    """
    Default Models Functions
    """
    @api.multi
    def _validate_data(self, value):
        msg , filterFloat = {}, {}
        
        if not value.get('for_bidding'):
            filterFloat['Quantity'] = value.get('qty', False)

        filterFloat['Weight/pcs'] = value.get('weight_per_pcs', False)
       
        msg.update(validator._validate_number(filterFloat))
        validator.validation_msg(msg)
        
        return True
    
    @api.multi
    def _check_sum_percentage(self, vals):
        
        yarn = vals.get('yarn_ids', False)
        accessories = vals.get('accessories_ids', False)
        if yarn:
            sum = 0
            for val in yarn:
                for line in val:
                    if type(line) is dict:
                        sum = sum + line['percentage']
                if sum > 100:
                    raise osv.except_osv(('Validation Error'), (validator.msg['percent_100']))
        
    @api.model
    def create(self, vals):
        self._validate_data(vals)
#         self._check_sum_percentage(vals)
        version = vals.get('version', 0)
        print version
        if (version in [0, 1]):
            vals['name'] = self.env['ir.sequence'].get('procos_code')
          
        return super(ProductCosting, self).create(vals)
    
    
    @api.multi
    def write(self, vals):
#         self._validate_data(vals)
#         self._check_sum_percentage(vals)
        return super(ProductCosting, self).write(vals)
 
         
    @api.one
    def costing_copy(self, default=None):
        
        default = dict(default or {})
        if default['create_version']:
            default['version'] = self.version + 1
            default['ref_costing_id'] = self.id
            default['name'] = self.name
        else:
            print "create version"
            default['costing_id'] = ''
            default['version'] = 1
            default['name'] = ''

        res = super(ProductCosting, self).copy(default)
        
        # Update the current record
        if default['create_version']:
            self.write({'product_costing_visible':False, 'costing_id':res.id})
            for st in self.costing_ids:
                st.write({'costing_id':res.id})
        
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'src_model': 'product.costing',
            'res_model': 'product.costing',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': res.id
        }
    
    @api.multi    
    def copy_quotation(self, cr, uid, ids, context=None):
        id = self.copy(cr, uid, ids[0], context=context)
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'product', 'product_costing_view_form')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': _('Product Costing'),
            'res_model': 'product.costing',
            'res_id': id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
    }
    
    def _get_default_uom(self, name):
        res = self.env['product.uom'].search([('name', '=like', name)])
        return res and res[0] or False
    
    def _get_default_currency(self, name):
        res = self.env['res.currency'].search([('name', '=like', name)])
        return res and res[0] or False
    
    """
    Computed Function for Various Fields 
    """
    @api.multi
    @api.depends('yarn_ids')
    def _compute_yarn_sum_percentage(self):
        if self.yarn_ids:
            sum = 0
            for val in self.yarn_ids:
                    sum = sum + val.percentage
            if sum > 100:
                raise osv.except_osv(('Validation Error'), (validator.msg['percent_100']))
            
    @api.multi
    @api.depends('yarn_ids', 'product_currency_id', 'weight_per_pcs')
    def _compute_yarn_cost(self):
        result = {}
        for costing in self:
            total = 0.0
            for line in costing.yarn_ids:
                total += line.cost_selected_curr
            result[costing.id] = total
        self.total_yarn_cost = total
        
    @api.multi
    @api.depends('accessories_ids', 'product_currency_id', 'weight_per_pcs')
    def _compute_total_accessories_cost(self):
        result = {}
        for costing in self:
            total = 0.0
            for line in costing.accessories_ids:
                total += line.cost_selected_curr
            result[costing.id] = total
        self.total_accessories_cost = total
        
    @api.multi
    @api.depends('cm_ids', 'product_currency_id', 'total_cm_cost_usd')
    def _compute_cm_costs(self):
        self.total_cm_cost = self.total_cm_cost_usd
            
    @api.one
    @api.depends('grand_total')
    def _computed_fob_cost(self):
        self.fob_cost = self.grand_total / 12 
    
    @api.multi
    @api.depends('weight_type', 'weight_per_pcs')
    def _compute_weight_per_dzn(self):
        if self.weight_type == 'pcs':
            self.weight_per_dzn = self.weight_per_pcs *12
        elif self.weight_type == 'dzn':
            self.weight_per_dzn = self.weight_per_pcs


    """
    Onchange fields 
    """
    @api.onchange('weight_type', 'weight_per_pcs', 'product_currency_id')
    def _onchange_weight_per_pcs(self):
        
        if self.yarn_ids:
            for line in self.yarn_ids:
                line.weight = (line.percentage * (line.yarn_costing_id.weight_per_dzn) / 100)
                line.wastage_quantity = (line.weight * line.wastage_percentage) / 100  
                line.total_qty_required = line.weight + line.wastage_quantity
                line.total_cost = line.total_qty_required * line.yarn_rate
                
                if  line.yarn_costing_id.product_currency_id:
                    rate = (line.yarn_rate * (line.percentage / 100))
                    line.yarn_rate_selected_curr = rate / line.convert_currency(line.yarn_costing_id.product_currency_id.id, line.line_currency_id.id)  
                    line.cost_selected_curr = line.total_cost / line.convert_currency(line.yarn_costing_id.product_currency_id.id, line.line_currency_id.id)        
        if self.accessories_ids:
            for line in self.accessories_ids:
                line.wastage_quantity = (line.quantity * line.wastage_percentage) / 100 
                line.total_cost = line.total_qty_required * line.yarn_rate
                if  line.accessories_costing_id.product_currency_id:
                    line.cost_selected_curr = line.total_cost / line.convert_currency(line.accessories_costing_id.product_currency_id.id, line.line_currency_id.id)        
        if self.cm_ids:
            for cm in self.cm_ids:
                if cm.total_cost and cm.line_currency_id and cm.cm_costing_id.product_currency_id:
                    cm.total_cost_usd = cm.total_cost / cm.convert_currency(cm.cm_costing_id.product_currency_id.id, cm.line_currency_id.id)        

        
    @api.onchange('buyer_id')
    def _onchange_buyer_id(self):
        res, ids = {}, []
        self.style_id = 0
        self.dept_id = 0
        self.product_size_group_id = 0
        self.buyer_ref = self.buyer_id.name
        
        if self.buyer_id:
            for obj in self.buyer_id.styles_ids:
                if obj.visible == True and obj.state == 'confirm':
                    ids.append(obj.id)
        
        res['domain'] = {
                    'style_id':[('id', 'in', ids)],
                }
        return res 

    """
    Summary Computed Functions
    """
    @api.one
    @api.depends('total_summary_cost', 'commercial_cost_percentage')
    def _compute_commercial_cost(self):
        self.commercial_cost = (self.total_summary_cost * (self.commercial_cost_percentage / 100))
        
    @api.one
    @api.depends('total_summary_cost', 'profit_percentage')
    def _compute_proifit(self):
        self.profit = (self.total_summary_cost * (self.profit_percentage / 100))
    
    @api.one
    @api.depends('total_summary_cost', 'commercial_cost', 'profit')
    def _compute_total_head_commission(self):
        self.total_head_commission = (self.total_summary_cost + self.commercial_cost + self.profit)    
    
    
    @api.one
    @api.depends('total_head_commission', 'buying_house_percentage')
    def _compute_buying_house_commission(self):
        self.buying_house_commission = self.total_head_commission * (self.buying_house_percentage / 100)
        
    @api.one
    @api.depends('total_head_commission', 'buying_house_commission')
    def _computed_grand_total(self):
        self.grand_total = self.total_head_commission + self.buying_house_commission
    
    @api.multi
    @api.depends('total_yarn_cost', 'linking_yarn_cost', 'total_accessories_cost', 'fabric_cost', 'embrodery_cost', 'fabric_cost', 'embrodery_cost', 'print_cost', 'lab_test_cost', 'total_cm_cost')
    def _compute_total_summary_cost(self):
        self.total_summary_cost = (self.total_yarn_cost + self.linking_yarn_cost + self.total_accessories_cost + 
        self.fabric_cost + self.embrodery_cost + self.print_cost + self.lab_test_cost + self.total_cm_cost)
    
    """
    CM Calculation Computed Functions
    """
    @api.multi
    @api.depends('cm_ids', 'fixed_overhead_bonus_percentage', 'fixed_overhead_currency_id')
    def _compute_fixed_overhead_cm_cost_usd(self):
        sum_cost = 0
        if self.cm_ids: 
            sum_cost = sum([x.total_cost_usd for x in self.cm_ids])
            self.fixed_overhead_cm_cost_usd = sum_cost * (self.fixed_overhead_bonus_percentage / 100)
            
    @api.multi
    @api.depends('cm_ids', 'fixed_overhead_bonus_percentage', 'fixed_overhead_currency_id')
    def _compute_fixed_overhead_cm_cost_bdt(self):
        sum_cost = 0
        if self.cm_ids: 
            sum_cost = sum([x.total_cost for x in self.cm_ids])
            self.fixed_overhead_cm_cost_bdt = sum_cost * (self.fixed_overhead_bonus_percentage / 100)
            
    @api.multi
    @api.depends('cm_ids', 'fixed_overhead_cm_cost_usd')
    def _compute_total_cm_cost_usd(self):
        sum_cost = 0
        if self.cm_ids: 
            self.total_cm_cost_usd = sum([x.total_cost_usd for x in self.cm_ids]) + self.fixed_overhead_cm_cost_usd
            
    @api.multi
    @api.depends('cm_ids', 'fixed_overhead_cm_cost_bdt')
    def _compute_total_cm_cost_bdt(self):
        sum_cost = 0
        if self.cm_ids: 
            self.total_cm_cost_bdt = sum([x.total_cost for x in self.cm_ids]) + self.fixed_overhead_cm_cost_bdt       
            
    """       
    State Actions
    """    
    def action_draft(self):
        self.state = 'draft'
    
    @api.one
    def action_confirm(self):
        self.state = 'confirm'
    
    @api.one
    def action_approve(self):
        self.state = 'approve'
    
    @api.one
    def action_reject(self):
        self.state = 'reject'
    
    @api.one
    def action_revise(self):
        self.state = 'draft'
    
    @api.one
    def action_cancel(self):
        self.state = 'cancel'
