from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class InheritedPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def action_view_invoice(self):
        result = super(InheritedPurchaseOrder, self).action_view_invoice()
        result['context']['default_from_po_form'] = True
        pickings = self.env['stock.picking'].search(
            ['|', ('origin', '=', self.name), ('origin', '=', self.po_lc_id.name),
             ('check_mrr_button', '=', True)])
        if not pickings and not self.cnf_quotation and not self.is_service_order:
            raise UserError(_('No MRR completed for this order!'))

        moves = self.env['stock.move'].search(
            [('picking_id', 'in', pickings.ids), ('state', '=', 'done')])
        total_mrr_qty = float("{:.4f}".format(sum(move.product_qty for move in moves)))


        return result
