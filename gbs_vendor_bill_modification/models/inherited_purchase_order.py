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

        result['context']['purchase_order'] = self.id
        result['context']['invoice_type'] = 'in_invoice'
        # result['context']['default_pickings'] = pickings.ids
        # is_after_automation = False
        # if self.env.user.company_id.mrr_bill_automation_date < self.date_order:
        #     pickings_ids = []
        #     for picking in pickings:
        #         moves = self.env['stock.move'].search(
        #             [('picking_id', 'in', picking.ids), ('state', '=', 'done')])
        #         for move in moves:
        #             if float("{:.4f}".format(move.available_qty)) != 0:
        #                 if picking.id not in pickings_ids:
        #                     pickings_ids.append(picking.id)
        #     result['context']['default_pickings'] = pickings_ids
        #
        #     is_after_automation = True
        # result['context']['default_is_after_automation'] = is_after_automation

        return result
