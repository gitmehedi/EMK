from odoo import models, fields, api

class InheritStockPicking(models.Model):
    _inherit = 'stock.picking'

    delivery_order_id = fields.Many2one('delivery.order.layer', string='D.O No.', readonly=True)
    lc_id = fields.Many2one('letter.credit', string='L/C No', readonly=True, compute="_calculate_lc_id", store=False)

    @api.multi
    def _calculate_lc_id(self):
        self.lc_id = self.delivery_order_id.sale_order_id.lc_id.id


class InheritStockMove(models.Model):
    _inherit = 'stock.move'

    delivery_order_id = fields.Many2one('delivery.order.layer', string='D.O No.', readonly=True)


