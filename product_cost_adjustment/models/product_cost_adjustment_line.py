from openerp import api, fields, models



class ProductCostAdjustmentLine(models.Model):
    _name = 'product.cost.adjustment.line'

    product_id = fields.Many2one('product.product', string="Product")
    cost_adjustment_id = fields.Many2one('product.cost.adjustment', string="List")
    old_cost_price = fields.Integer(compute='_compute_old_price')
    new_cost_price = fields.Integer(string="New Price")
    cost_adjustment_id = fields.Many2one('product.cost.adjustment.line', 'cost_adjustment_id')


    @api.multi
    def _compute_old_price(self):
        if self.product_id:
            self.old_cost_price = self.product_id.standard_price

