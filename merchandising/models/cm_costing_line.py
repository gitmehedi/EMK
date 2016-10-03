from openerp import api, fields, models 
from openerp.addons.helper import validator

class CmCostingLine(models.Model):
    """
    CM Costing Line
    """
    _name = "cm.costing.line"
    
    standard_wage = fields.Float(digits=(20, 2), string='Standard Wage', default=None)
    percentage = fields.Float(digits=(20, 2), string='Percentage', default=None)
    amount = fields.Float(compute="_compute_amount", digits=(20, 2), string='Amount', default=None)
    bonus = fields.Float(digits=(20, 2), string='Bonus%', default=None)
    bonus_amount = fields.Float(compute="_compute_bonus_amount", digits=(20, 2), string='Bonus Amount', default=None)
    productivity = fields.Float(digits=(20, 4), string='Productivity', default=None)

    total_cost = fields.Float(digits=(20, 4), string='Total Cost')
    total_cost_usd = fields.Float(compute="_compute_total_cost_usd", digits=(20, 4), string='Cost in USD')
    
    # relational fields
    
    product_id = fields.Many2one('product.template', string="Product", required=True, domain=[('type', '=', 'service')])
    cm_costing_id = fields.Many2one('product.costing', string="CM", ondelete='set null')
    line_currency_id = fields.Many2one('res.currency', string="Currency", required=True, default=lambda self: self._get_default_currency('USD'))
    
    """
    Default Functionality of Models
    """
    @api.multi
    def _validate_data(self, value):
        msg , filterPer, filterNum = {}, {}, {}
        
        filterNum['Standard Wage'] = value.get('standard_wage', False)
        filterNum['Productivity'] = value.get('productivity', False)
        filterPer['Bonus'] = value.get('bonus', False)
        filterPer['Percentage'] = value.get('percentage', False)
       
        msg.update(validator._validate_percentage(filterPer))
        msg.update(validator._validate_number(filterNum))
        validator.validation_msg(msg)
        
        return True
    
    @api.model
    def create(self, vals):
        self._validate_data(vals)
        return super(CmCostingLine, self).create(vals)
    
    @api.multi
    def write(self, vals):
        self._validate_data(vals)
        return super(CmCostingLine, self).write(vals)
    
    def _get_default_currency(self, name):
        res = self.env['res.currency'].search([('name', '=like', name)])
        return res and res[0] or False
    
    """
    Computed Fields
    """
    @api.depends('standard_wage', 'productivity')
    def _compute_amount(self):
        for cm in self:
            if cm.standard_wage and cm.productivity:
                cm.amount = (cm.standard_wage / cm.productivity) 
                
                
    @api.depends('amount', 'bonus')
    def _compute_bonus_amount(self):
        for cm in self:
            if cm.amount and cm.bonus:
                cm.bonus_amount = (cm.amount * (cm.bonus / 100))
    
    @api.onchange('amount', 'bonus_amount')
    def onchange_total_cost(self):
        for cm in self:
            if cm.amount and cm.bonus_amount:
                cm.total_cost = cm.amount + cm.bonus_amount      
    
    @api.depends('total_cost', 'line_currency_id')
    def _compute_total_cost_usd(self):
        for cm in self:
            if cm.total_cost and cm.line_currency_id and cm.cm_costing_id.product_currency_id:
                cm.total_cost_usd = cm.total_cost / cm.convert_currency(cm.cm_costing_id.product_currency_id.id, cm.line_currency_id.id)  
            
   
    
    @api.model
    def convert_currency(self, from_cur, to_cur):
        currency_obj = self.env['res.currency']
        t_cur, f_cur = 0, 0
        if from_cur:
            f_cur = currency_obj.search([('id', '=', from_cur)], limit=1)
        
        if to_cur:
            t_cur = currency_obj.search([('id', '=', to_cur)], limit=1)    
        return t_cur.rate_silent / f_cur.rate_silent
        
    
