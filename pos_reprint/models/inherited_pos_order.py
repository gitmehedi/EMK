from odoo import models, fields, api, _
from odoo.exceptions import Warning


class InheritedPosOrder(models.Model):
    _inherit = 'pos.order'

    return_pos_ref = fields.Char(string="PoS Reference", required=False)
    order_id = fields.Many2one('pos.order', required=False)

    @api.model
    def action_pos_order_delete(self):
        if 'Point of Sale Admin' not in [val.name for val in self.env.user.groups_id]:
            raise Warning(_('Only Point of Sale Admin can delete Point of Sale Order. Please contact with Admin.'))

        self.state = 'cancel'
        if self.state == 'cancel':
            self.unlink()

    def refund(self, cr, uid, ids, context=None):
        """Create a copy of order  for refund order"""
        clone_list = []
        line_obj = self.pool.get('pos.order.line')

        for order in self.browse(cr, uid, ids, context=context):
            current_session_ids = self.pool.get('pos.session').search(cr, uid, [
                ('state', '!=', 'closed'),
                ('user_id', '=', uid)], context=context)
            if not current_session_ids:
                raise models.except_models(_('Error!'), _(
                    'To return product(s), you need to open a session that will be used to register the refund.'))

            clone_id = self.copy(cr, uid, order.id, {
                'name': order.name + ' REFUND',  # not used, name forced by create
                'session_id': current_session_ids[0],
                'return_pos_ref': order.pos_reference,
                'order_id': order.id,
            }, context=context)
            clone_list.append(clone_id)

        for clone in self.browse(cr, uid, clone_list, context=context):
            clone.lines = []
            for order_line in clone.lines:
                line_obj.unlink(cr, uid, [order_line.id], context=context)

                # def unlink(self, cr, uid, ids, context=None):

        return clone_list[0]


class InheritedPosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    def _check_return_prouduct_qty(self, cr, uid, ids, context=None):

        record = self.browse(cr, uid, ids, context=context)
        if record.qty < 0:
            order = self.pool.get('pos.order.line').search(cr, uid, [('product_id', '=', record.product_id.id),
                                                                     ('order_id', '=', record.order_id.order_id.id)])
            if not order:
                return False
        return True


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    available_in_pos = fields.Boolean(default=False)
