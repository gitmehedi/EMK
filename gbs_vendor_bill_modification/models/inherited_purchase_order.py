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
        result['context']['default_purchase_id'] = self.id
        result['context']['invoice_type'] = 'in_invoice'

        return result
