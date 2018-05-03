from odoo import models, fields, api

class InheritStockPicking(models.Model):
    _inherit = 'stock.picking'

    delivery_order_id = fields.Many2one('delivery.order.layer', string='D.O No.', readonly=True)
    lc_id = fields.Many2one('letter.credit', string='L/C No', readonly=True)



class InheritStockMove(models.Model):
    _inherit = 'stock.move'

    delivery_order_id = fields.Many2one('delivery.order.layer', string='D.O No.', readonly=True)


