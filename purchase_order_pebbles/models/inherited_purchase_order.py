from openerp import api, fields, models, _
from openerp.exceptions import ValidationError


class InheritedPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_picking_create(self, cr, uid, ids, context=None):
        return True

    def action_invoice_create(self, cr, uid, ids, context=None):
        """Generates invoice for given ids of purchase orders and links that invoice ID to purchase order.
        :param ids: list of ids of purchase orders.
        :return: ID of created invoice.
        :rtype: int
        """

    @api.one
    def action_purchase_done(self, context=None):
        if self.state == 'approved':
            self.write({'state': 'done'})
        else:
            raise ValidationError(_("Purchse Order must in [Approved] state."))
