from openerp import api, fields, models

class InheritedStockQuant(models.Model):
    _inherit = 'stock.quant'
    
    @api.one
    @api.depends('cost', 'qty')
    def _cal_subtotal(self):
        self.sub_total = self.cost * self.qty
    
    sub_total = fields.Float('Subtotal', compute='_cal_subtotal', store=True)
    