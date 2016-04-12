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
    qty_dk= fields.Float('Opening Stock')
    qty_in_tk= fields.Float('Stock In')
    qty_out_tk= fields.Float('Stock Out')
    qty_ck= fields.Float('Closing Stock')
    val_dk= fields.Float('Opening Stock Value', default=0.0)
    val_in_tk= fields.Float('Stock In Value',  default=0.0)
    val_out_tk= fields.Float('Stock Out Value', default=0.0)
    val_ck= fields.Float('Closing Stock Value',  default=0.0)
#     val_dk= fields.Float('Opening Stock Value', compute='_computed_val_dk', default=0.0)
#     val_in_tk= fields.Float('Stock In Value', compute='_computed_val_in_tk', default=0.0)
#     val_out_tk= fields.Float('Stock Out Value', compute='_computed_val_out_tk', default=0.0)
#     val_ck= fields.Float('Closing Stock Value', compute='_computed_val_ck', default=0.0)
    
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