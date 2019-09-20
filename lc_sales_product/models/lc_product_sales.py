from odoo import api, fields, models,_

class LCProduct(models.Model):
    _inherit = 'lc.product.line'

    delivered_qty =  fields.Float(string='Delivered',compute = '_compute_delivered_qty',store=False)

    @api.one
    def _compute_delivered_qty(self):
        for pi_id in self.lc_id.pi_ids_temp:
            so_ids = self.env['sale.order'].search([('pi_id', '=', pi_id.id)])
            for so_id in so_ids:
                quantity = so_id.order_line.filtered(lambda x: x.product_id.id == self.product_id.id).qty_delivered
                self.delivered_qty = self.delivered_qty + quantity


