from openerp import api, exceptions, fields, models
# from openerp import api, fields, models
from openerp import tools
from datetime import datetime

class StockInventory(models.Model):
    
    _name = 'stock.inventory.report'
    _auto = False
    
    id= fields.Integer('Sequence')
    product_id= fields.Integer('Product id')
    name= fields.Char('Product')
    code= fields.Char('Code')
    category = fields.Char('Category')
    uom = fields.Char('UoM')
    qty_dk= fields.Float('Opening Stock')
    qty_in_tk= fields.Float('Stock In')
    qty_out_tk= fields.Float('Stock Out')
    qty_ck= fields.Float('Closing Stock')
    val_dk= fields.Float('OS Value', default=0.0)
    val_in_tk= fields.Float('SI Value',  default=0.0)
    val_out_tk= fields.Float('SO Value', default=0.0)
    val_ck= fields.Float('CS Value',  default=0.0)
    avg_cost_dk= fields.Float('OS Cost', compute='_computed_avg_cost_dk', default=0.0)
    avg_cost_in_tk= fields.Float('SI Cost', compute='_computed_avg_cost_in_tk', default=0.0)
    avg_cost_out_tk= fields.Float('SO Cost', compute='_computed_avg_cost_out_tk', default=0.0)
    avg_cost_ck= fields.Float('CS Cost', compute='_computed_avg_cost_ck', default=0.0)
#     val_dk= fields.Float('Opening Stock Value', compute='_computed_val_dk', default=0.0)
#     val_in_tk= fields.Float('Stock In Value', compute='_computed_val_in_tk', default=0.0)
#     val_out_tk= fields.Float('Stock Out Value', compute='_computed_val_out_tk', default=0.0)
#     val_ck= fields.Float('Closing Stock Value', compute='_computed_val_ck', default=0.0)
    
    @api.multi
    @api.depends('product_id','qty_dk','val_dk')
    def _computed_avg_cost_dk(self):
        res = 0.0
        for line in self:
            if line.product_id and line.qty_dk and line.val_dk:
                res = line.val_dk / line.qty_dk
                line.avg_cost_dk = res
    
    @api.multi
    @api.depends('product_id','qty_in_tk','val_in_tk')
    def _computed_avg_cost_in_tk(self):
        res = 0.0
        for line in self:
            if line.product_id and line.qty_in_tk and line.val_in_tk:
                res = line.val_in_tk / line.qty_in_tk
                line.avg_cost_in_tk = res
                
    @api.multi
    @api.depends('product_id','qty_out_tk','val_out_tk')
    def _computed_avg_cost_out_tk(self):
        res = 0.0
        for line in self:
            if line.product_id and line.qty_out_tk and line.val_out_tk:
                res = line.val_out_tk / line.qty_out_tk
                line.avg_cost_out_tk = res
    
    @api.multi
    @api.depends('product_id','qty_ck','val_ck')
    def _computed_avg_cost_ck(self):
        res = 0.0
        for line in self:
            if line.product_id and line.qty_ck and line.val_ck:
                res = line.val_ck / line.qty_ck
                line.avg_cost_ck = res            
    
    """
    @api.multi
    @api.depends('product_id','qty_dk')
    def _computed_val_dk(self):
        from_date = self._context['form']['date_from']
        to_date = self._context['form']['date_to']
        
        for line in self:
            res = 0.0
            cost_price_dk = 0.0
            if line.product_id and line.qty_dk:
                
                product_obj = self.env['product.template'].search([['id','=',line.product_id]])
                pro_his_pri_obj = self.env['product.price.history'].search([['product_template_id','=',product_obj.id],['datetime','<=',from_date]],limit=1)
                
                cost_price_dk = pro_his_pri_obj.cost or 0.0
                res = line.qty_dk * cost_price_dk
                line.val_dk = res

    @api.multi
    @api.depends('product_id','qty_in_tk')
    def _computed_val_in_tk(self):
        from_date = self._context['form']['date_from']
        to_date = self._context['form']['date_to']
        print "=======from_date====",from_date
        print "=======to_date====",to_date
        for line in self:
            res = 0.0
            cost_price_dk = 0.0
            if line.product_id and line.qty_in_tk:
                product_obj = self.env['product.template'].search([['id','=',line.product_id]])
                print "-----product_template_id---",product_obj.id
                print "-----line.qty_dk---",line.qty_dk
                cost_price_dk = product_obj.standard_price or 0.0
                res = line.qty_in_tk * cost_price_dk
                line.val_in_tk = res

    @api.multi
    @api.depends('product_id','qty_out_tk')
    def _computed_val_out_tk(self):
        for line in self:
            res = 0.0
            cost_price_dk = 0.0
            if line.product_id and line.qty_out_tk:
                product_obj = self.env['product.template'].search([['id','=',line.product_id]])
                cost_price_dk = product_obj.standard_price or 0.0
                res = line.qty_out_tk * cost_price_dk
                line.val_out_tk = res

    @api.multi
    @api.depends('product_id','qty_ck')
    def _computed_val_ck(self):
        for line in self:
            res = 0.0
            cost_price_dk = 0.0
            if line.product_id and line.qty_ck:
                product_obj = self.env['product.template'].search([['id','=',line.product_id]])
                cost_price_dk = product_obj.standard_price or 0.0
                res = line.qty_ck * cost_price_dk
                line.val_ck = res
    """