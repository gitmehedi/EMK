from openerp import api, fields, models 
from openerp.addons.helper import validator

class ProductCostingAccessories(models.Model):
    """
    Product Costing Accessories
    """
    _name = "product.costing.accessories"
    
    """
    Fields
    """
    percentage = fields.Float(string='Percentage %', digits=(20, 2), required=True, default=0.0)
    wastage_percentage = fields.Float(string='Wastage %', digits=(20, 2),
                                       default=0.0, required=True,)
    yarn_rate = fields.Float(string='Item Rate', digits=(20, 4), required=True,)
    
    """
    Computed Fields
    """
    quantity = fields.Float(string='Quantity', digits=(20, 4), required=True)
    wastage_percentage = fields.Float(string='Wastage %', digits=(20, 2), required=True)
    wastage_quantity = fields.Float(compute="_compute_wastage_quantity", digits=(20, 4), store=True, string='Wastage Qty')
   
    total_qty_required = fields.Float(compute='_compute_total_yarn_required', digits=(20, 4),
                                       string='Total Item Req', store=True)
    
    cost_selected_curr = fields.Float(compute="_compute_cost_selected_currency", digits=(20, 4),
                                      string='Cost in Selected Currency', store=True)
    total_cost = fields.Float(compute='_compute_total_cost', digits=(20, 4),
                              string='Total Cost', store=True)
  
    """
    Relational Fields
    """
    product_id = fields.Many2one('product.product', string="Product", required=True)
    uom = fields.Many2one('product.uom', string="UoM")
    line_currency_id = fields.Many2one('res.currency', string="Currency", required=True, default=lambda self: self._get_default_currency('USD'))
    accessories_costing_id = fields.Many2one('product.costing', string="Accessories", delegate=True, ondelete='set null')
    
    """
    Default Functionality of Models
    """
    
    @api.multi
    def _validate_data(self, value):
        msg , filterPer, filterNum = {}, {}, {}
        
        filterPer['Wastage'] = value.get('wastage_percentage', False)
        filterPer['Percentage'] = value.get('percentage', False)
        filterNum['Item Rate'] = value.get('yarn_rate', False)
       
        msg.update(validator._validate_percentage(filterPer))
        msg.update(validator._validate_number(filterNum))
        validator.validation_msg(msg)
        
        return True
    
    @api.model
    def create(self, vals):
        self._validate_data(vals)
        return super(ProductCostingAccessories, self).create(vals)
    
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        return super(ProductCostingAccessories, self).write(vals)
    
    def _get_default_currency(self, name):
        res = self.env['res.currency'].search([('name', '=like', name)])
        return res and res[0] or False
    """
    Computed Fields
    """
    @api.depends('wastage_percentage', 'quantity')
    def _compute_wastage_quantity(self):
       for line in self:
            if line.quantity and line.wastage_percentage:
                line.wastage_quantity = (line.quantity * line.wastage_percentage) / 100 
#     @api.multi
    @api.depends('wastage_percentage', 'quantity')
    def _compute_total_yarn_required(self):
        
        for line in self:
            if line.quantity and line.wastage_quantity:
                line.total_qty_required = line.quantity + line.wastage_quantity
    
#     @api.multi
    @api.depends('total_qty_required', 'yarn_rate')
    def _compute_total_cost(self):
        
        for line in self:
            if line.total_qty_required and line.yarn_rate:
                line.total_cost = line.total_qty_required * line.yarn_rate
                                                                      
#     @api.multi
    @api.depends('total_cost', 'line_currency_id')
    def _compute_cost_selected_currency(self):
        
        for line in self:
            if line.total_cost and line.line_currency_id and line.accessories_costing_id.product_currency_id:
                line.cost_selected_curr = line.total_cost / line.convert_currency(line.accessories_costing_id.product_currency_id.id, line.line_currency_id.id)    
    
    @api.model
    def convert_currency(self, from_cur, to_cur):
        currency_obj = self.env['res.currency']
        t_cur, f_cur = 0, 0

        if from_cur:
            f_cur = currency_obj.search([('id', '=', from_cur)], limit=1)
        
        if to_cur:
            t_cur = currency_obj.search([('id', '=', to_cur)], limit=1)    

        return t_cur.rate_silent / f_cur.rate_silent
    
    
