from openerp import api, fields, models

class InheritedStockMove(models.Model):
    _inherit = 'stock.move'
    
    @api.one
    @api.depends('price_unit', 'product_qty')
    def _cal_subtotal(self):
        self.sub_total = self.price_unit * self.product_uom_qty
    
    sub_total = fields.Float('Subtotal', compute='_cal_subtotal', store=True)
    
#     @api.multi
#     def attribute_price(self):
#         """
#             Attribute price to move, important in inter-company moves or receipts with only one partner
#         """
#         for move in self:
#             if not move.price_unit or move.price_unit == 0:
#                 price = move.product_id.standard_price
#                 moe.write({'price_unit': price})