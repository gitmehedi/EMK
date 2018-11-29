from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # @api.multi
    # def action_view_mrr(self):
    #     action = self.env.ref('stock_picking_mrr.action_stock_picking_mrr')
    #     result = action.read()[0]
    #
    #     # override the context to get rid of the default filtering on picking type
    #     result.pop('id', None)
    #     result['context'] = {}
    #     pick_ids = sum([order.picking_ids.ids for order in self], [])
    #     # choose the view_mode accordingly
    #     if len(pick_ids) > 1:
    #         result['domain'] = "[('id','in',[" + ','.join(map(str, pick_ids)) + "])]"
    #     elif len(pick_ids) == 1:
    #         res = self.env.ref('stock.view_picking_form', False)
    #         result['views'] = [(res and res.id or False, 'form')]
    #         result['res_id'] = pick_ids and pick_ids[0] or False
    #     return result

