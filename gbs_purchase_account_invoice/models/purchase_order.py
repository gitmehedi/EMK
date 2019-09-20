from odoo import api, fields, models, _

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # @api.depends('order_id.state', 'move_ids.state')
    # def _compute_qty_received(self):
    #     data =  {d['id']: d['qty_received']for d in self.read(['qty_received'])}
    #     for record in self:
    #         if not data:
    #             super(PurchaseOrderLine, self)._compute_qty_received()
    #         else:
    #             record.qty_received = data