from openerp import api, fields, models 
from openerp.addons.helper import validator

class ProductCostingLine(models.Model):
    """
    Product Costing line
    """
    _name = "product.costing.line"
    
    """
    Fields
    """
    percentage = fields.Float(string='Percentage %', digits=(20, 2), required=True, default=0.0)
    wastage_percentage = fields.Float(string='Wastage %', digits=(20, 2),
                                       default=0.0, required=True,)
    company_current_rate = fields.Float(string='Current Rate', digits=(20, 4),)
    yarn_rate = fields.Float(string='Yarn Rate', digits=(20, 4), required=True,)
    
    """
    Computed Fields
    """
    weight = fields.Float(compute="_compute_weight", string='Weight', digits=(20, 4), store=True)
    wastage_percentage = fields.Float(string='Wastage %', digits=(20, 2), required=True)
    wastage_quantity = fields.Float(compute="_compute_wastage_quantity", digits=(20, 4), store=True, string='Wastage Qty')
   
    total_qty_required = fields.Float(compute='_compute_total_yarn_required', digits=(20, 4),
                                       string='Total Yarn Req', store=True)
    yarn_rate_selected_curr = fields.Float(compute="_compute_yarn_rate_selected_currency", digits=(20, 4),
                                           string='Yarn Rate in Selected Currency', store=True)
    cost_selected_curr = fields.Float(compute="_compute_cost_selected_currency", digits=(20, 4),
                                      string='Cost in Selected Currency', store=True)
    total_cost = fields.Float(compute='_compute_total_cost', digits=(20, 4),
                              string='Total Cost', store=True)
  
    """
    Relational Fields
    """
    product_id = fields.Many2one('product.product', string="Product", required=True)
    uom = fields.Many2one('product.uom', string="UoM")
    line_currency_id = fields.Many2one('res.currency', string="Currency", required=True, default=lambda self: self._get_default_currency('USD'),)
    company_currency_id = fields.Many2one('res.currency', string="Company Currency ID", default=lambda self: self.env.user.company_id.currency_id.id)
    yarn_costing_id = fields.Many2one('product.costing', string="Yarn", ondelete='set null')
    accessories_costing_id = fields.Many2one('product.costing', string="Accessories", ondelete='set null')
    
    
    """
    Default Functionality of Models
    """
    @api.multi
    def _validate_data(self, value):
        msg , filterPer, filterNum = {}, {}, {}
        
        filterPer['Wastage'] = value.get('wastage_percentage', False)
        filterPer['Percentage'] = value.get('percentage', False)
        filterNum['Yarn Rate'] = value.get('yarn_rate', False)
       
        msg.update(validator._validate_percentage(filterPer))
        msg.update(validator._validate_number(filterNum))
        validator.validation_msg(msg)
        
        return True
    
    @api.model
    def create(self, vals):
        self._validate_data(vals)
        return super(ProductCostingLine, self).create(vals)
    
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        return super(ProductCostingLine, self).write(vals)
    
    def _get_default_currency(self, name):
        res = self.env['res.currency'].search([('name', '=like', name)])
        return res and res[0] or False
    """
    Computed Fields
    """            
    
    @api.depends('percentage', 'wastage_percentage')
    def _compute_weight(self):
        for line in self:  
            if line.percentage and line.yarn_costing_id.weight_per_dzn: 
                line.weight = (line.percentage * (line.yarn_costing_id.weight_per_dzn) / 100)
    
#     @api.multi
    @api.depends('weight', 'wastage_percentage')
    def _compute_wastage_quantity(self):
        for line in self:
            if line.weight and line.wastage_percentage:
                line.wastage_quantity = (line.weight * line.wastage_percentage) / 100    
        
#     @api.multi
    @api.depends('percentage', 'wastage_percentage', 'weight', 'wastage_quantity')
    def _compute_total_yarn_required(self):
        
        for line in self:
            if line.weight:
                line.total_qty_required = line.weight + line.wastage_quantity
    
#     @api.multi
    @api.depends('total_qty_required', 'yarn_rate')
    def _compute_total_cost(self):
        
        for line in self:
            if line.total_qty_required and line.yarn_rate:
                line.total_cost = line.total_qty_required * line.yarn_rate
        
#     @api.multi
    @api.depends('yarn_rate', 'percentage', 'line_currency_id')
    def _compute_yarn_rate_selected_currency(self):
        
        for line in self:
            if line.total_cost and line.line_currency_id and line.yarn_costing_id.product_currency_id:
                rate = (line.yarn_rate * (line.percentage / 100)) 
                line.yarn_rate_selected_curr = rate / self.convert_currency(line.yarn_costing_id.product_currency_id.id, line.line_currency_id.id)  
                                                                      
#     @api.multi
    @api.depends('total_cost', 'line_currency_id')
    def _compute_cost_selected_currency(self):
        
        for line in self:
            if line.total_cost and line.line_currency_id and line.yarn_costing_id.product_currency_id:
                line.cost_selected_curr = line.total_cost / self.convert_currency(line.yarn_costing_id.product_currency_id.id, line.line_currency_id.id)    
    
#     @api.multi    
#     def calculate_total_qty_required(self):
#         if self.weight > 0:
#             self.total_qty_required = self.weight + self.wastage_quantity
    
#     @api.onchange('wastage_quantity_temp')
#     def onchange_wastage_quantity(self):
#         if self.weight > 0 and self.quantity_flag:
#             self.wastage_quantity = self.wastage_quantity_temp
#             self.wastage_percentage = (self.wastage_quantity * 100.0) / self.weight
#             self.wastage_percentage_temp = self.wastage_percentage
#             self.parcantage_flag = False
#             self.quantity_flag = True
#             self.total_qty_required = self.weight + self.wastage_quantity_temp
#             self.total_cost = self.total_qty_required * self.unit_price
#             
#     @api.onchange('wastage_percentage_temp')
#     def onchange_wastage_percentage(self):
#         if self.weight > 0 and self.parcantage_flag:
#             self.wastage_percentage = self.wastage_percentage_temp
#             self.wastage_quantity = (self.weight * self.wastage_percentage) / 100.0
#             self.wastage_quantity_temp = self.wastage_quantity
#             self.quantity_flag = False
#             self.parcantage_flag = True
#             self.total_qty_required = self.weight + self.wastage_quantity_temp
#             self.total_cost = self.total_qty_required * self.unit_price
    
 
            
   
                
#     @api.multi
#     @api.depends('weight', 'unit_price', 'line_currency_id')
#     def _compute_total_cost_(self):
#         costing_yarn_sum = 0.0
#         for line in self:
#             if line.weight > 0:
#                 line.wastage_percentage = (line.wastage_quantity * 100.0) / line.weight
#                 
#             line.wastage_quantity = (line.weight * line.wastage_percentage) / 100.0
#                 
#             line.calculate_total_qty_required()
#             
#             line.line_current_rate = line.line_currency_id.rate_silent
#             
#             line.company_current_rate = line.company_currency_id.rate_silent
# 
#             
#             costing_flag = 0
#             # For yarn_costing_id
#             if line.line_current_rate > 0 and line.yarn_costing_id.product_currency_id.rate_silent > 0 :
#                 line.converted_price = (1 / line.line_current_rate) * (1 / line.yarn_costing_id.product_currency_id.rate_silent) * line.unit_price
#                 costing_flag = 1
#             # For accessories_costing_id
#             if line.line_current_rate > 0 and line.accessories_costing_id.product_currency_id.rate_silent > 0:
#                 line.converted_price = (1 / line.line_current_rate) * (1 / line.accessories_costing_id.product_currency_id.rate_silent) * line.unit_price
#                 costing_flag = 2
#             line.total_cost = line.total_qty_required * line.converted_price
#             # costing_yarn_sum = costing_yarn_sum + line.total_cost
#             if line.total_cost > 0 and costing_flag == 1:
#                 line.yarn_costing_id.yarn_amount_flag = True
#             if line.total_cost > 0 and costing_flag == 2:
#                 line.accessories_costing_id.accessories_amount_flag = True
               
        # print costing_yarn_sum
        # line.yarn_costing_id.total_yarn_cost = costing_yarn_sum
   
#     @api.multi    
#     def calculate_total_qty_required(self):
#         if self.weight > 0:
#             self.total_qty_required = self.weight + self.wastage_quantity
            
            
    @api.model
    def convert_currency(self, from_cur, to_cur):
        currency_obj = self.env['res.currency']
        t_cur, f_cur = 0, 0
        if from_cur:
            f_cur = currency_obj.search([('id', '=', from_cur)], limit=1)
        
        if to_cur:
            t_cur = currency_obj.search([('id', '=', to_cur)], limit=1)    
        return t_cur.rate_silent / f_cur.rate_silent
    
    
