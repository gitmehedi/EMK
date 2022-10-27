from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class Utility(models.TransientModel):
    _name = 'account.invoice.utility'

    def get_available_qty(self, order_id, line_product_id, mrr_qty):
        other_invoices = order_id.invoice_ids.filtered(lambda x: x.state != 'cancel')
        pro_qty_invoiced = 0
        for inv in other_invoices:
            for line in inv.invoice_line_ids:
                if line.product_id.id == line_product_id:
                    pro_qty_invoiced = pro_qty_invoiced + line.quantity
        available_qty = mrr_qty - pro_qty_invoiced
        available_qty = float("{:.4f}".format(available_qty))
        return available_qty

    def get_mrr_qty(self, order_id, lc_number, line_product_id):
        pickings = self.env['stock.picking'].search(
            ['|', ('origin', '=', order_id.name), ('origin', '=', lc_number),
             ('check_mrr_button', '=', True)])
        moves = self.env['stock.move'].search(
            [('picking_id', 'in', pickings.ids), ('product_id', 'in', line_product_id.ids),
             ('state', '=', 'done')])
        total_mrr_qty = sum(move.product_qty for move in moves)
        # if total_mrr_qty <= 0:
        #     raise UserError(_('MRR not done for this order!'))
        return total_mrr_qty
