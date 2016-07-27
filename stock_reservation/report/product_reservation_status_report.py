from openerp import api, exceptions, fields, models
from openerp import tools
from datetime import datetime

class ProductReservationStatus(models.Model):
    
    _name = 'product.reservation.status.report'
    _auto = False
    
    id= fields.Integer('Product Id')
    product_name= fields.Char('Product')
    quantity= fields.Float('Reserve Qty')
    location_name= fields.Char('Location')
    epo_no = fields.Char('EPO No')

    """
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