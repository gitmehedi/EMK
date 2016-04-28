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
    bonus = fields.Float(digits=(20, 2), string='Bonus(%)', default=None)
    bonus_amount = fields.Float(compute="_compute_bonus_amount", digits=(20, 2), string='Bonus Amount', default=None)
    productivity = fields.Float(digits=(20, 4), string='Productivity', default=None)

    product_costing_type = fields.Selection([('pcs','Pcs'),('dzn','Dzn')], string="Costing Type",required=True)

    total_cost = fields.Float(digits=(20, 4), string='Total Cost',store=True)
    total_cost_usd = fields.Float(compute="_compute_total_cost_usd", digits=(20, 4), string='Cost in USD')
    total_cost_flag = fields.Boolean(string=" ")
    
    """ relational fields """
    
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
    @api.depends('standard_wage', 'productivity','product_costing_type')
    def _compute_amount(self):
        for cm in self:
            pc_val =1
            if cm.product_costing_type=='pcs':
                pc_val=12

            if cm.standard_wage and cm.productivity:
                cm.amount = (cm.standard_wage / cm.productivity) * pc_val
                
    @api.depends('amount', 'bonus','product_costing_type')
    def _compute_bonus_amount(self):
        for cm in self:
            if cm.amount and cm.bonus:
                cm.bonus_amount = (cm.amount * (cm.bonus / 100))

    @api.onchange('product_costing_type','standard_wage','line_currency_id', 'productivity','amount','bonus_amount')
    def onchange_total_cost(self):
        for cm in self:
            if cm.amount:
                cm.total_cost = cm.amount + cm.bonus_amount


    @api.depends('product_costing_type','standard_wage','line_currency_id', 'productivity','amount','bonus_amount','total_cost')
    def _compute_total_cost_usd(self):
        for cm in self:
            if cm.line_currency_id and cm.cm_costing_id.product_currency_id:
                if not cm.total_cost_flag:
                    cm.total_cost_usd = (cm.amount + cm.bonus_amount) / cm.convert_currency(cm.cm_costing_id.product_currency_id.id, cm.line_currency_id.id)
                else:
                    cm.total_cost_usd = (cm.total_cost) / cm.convert_currency(cm.cm_costing_id.product_currency_id.id, cm.line_currency_id.id)



    """
    On Change functionality
    """

    @api.onchange('product_id')
    def onchange_product_id(self):
        for cm in self:
            self.product_costing_type = self.product_id.costing_type
            self.standard_wage = self.product_id.standard_wage
            self.productivity = self.product_id.productivity

    @api.onchange('total_cost_flag')
    def onchange_total_cost_flag(self):
        for cm in self:
            if self.total_cost_flag:
                self.percentage = 0
                self.standard_wage=0
                self.productivity=0
                self.amount=0
                self.bonus=0
                self.bonus_amount=0
                self.total_cost=0
                self.total_cost_usd=0

    
    @api.model
    def convert_currency(self, from_cur, to_cur):
        currency_obj = self.env['res.currency']
        t_cur, f_cur = 0, 0
        if from_cur:
            f_cur = currency_obj.search([('id', '=', from_cur)], limit=1)
        
        if to_cur:
            t_cur = currency_obj.search([('id', '=', to_cur)], limit=1)    
        return t_cur.rate / f_cur.rate
        
    
