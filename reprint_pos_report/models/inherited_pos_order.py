import time

from openerp import models, fields
from openerp.tools.translate import _
from openerp.osv import  osv


class InheritedPosOrder(models.Model):
    _inherit = 'pos.order'

    return_pos_ref = fields.Char(string="PoS Reference", required=False)
    order_id = fields.Many2one('pos.order', required=False)

    def refund(self, cr, uid, ids, context=None):
        """Create a copy of order  for refund order"""
        clone_list = []
        line_obj = self.pool.get('pos.order.line')

        for order in self.browse(cr, uid, ids, context=context):
            current_session_ids = self.pool.get('pos.session').search(cr, uid, [
                ('state', '!=', 'closed'),
                ('user_id', '=', uid)], context=context)
            if not current_session_ids:
                raise osv.except_osv(_('Error!'), _(
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

        abs = {
            'name': _('Return Products'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pos.order',
            'res_id': clone_list[0],
            'view_id': False,
            'context': context,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
        }
        return abs
