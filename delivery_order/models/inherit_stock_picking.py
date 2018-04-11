from odoo import models, fields, api

class InheritStockPicking(models.Model):
    _inherit = 'stock.picking'

    delivery_order_id = fields.Many2one('delivery.order.layer', string='D.O No.', readonly=True)



