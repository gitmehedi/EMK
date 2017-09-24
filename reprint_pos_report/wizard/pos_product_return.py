import time
import datetime

from openerp.osv import osv, fields
from openerp.tools.translate import _


class PosProductReturn(osv.osv_memory):
    _name = 'pos.product.return'
    _description = 'Point of Sale Product Return'

    _columns = {
        'product_ids': fields.many2many('product.product', string='Products', required=True),
    }

    def return_products(self, cr, uid, ids, context=None):
        obj = self.pool.get('pos.order')
        pos_line = self.pool.get('pos.order.line')
        refund = obj.refund(cr, uid, context['active_id'])

        records = self.browse(cr, uid, ids, {})
        for record in records.product_ids:
            ids = pos_line.search(cr, uid, [('order_id', '=', context['active_id']), ('product_id', '=', record.id)])
            ids = ids[0] if ids else []
            product = pos_line.browse(cr, uid, ids)

            rec = {}
            rec['name'] = record.name
            rec['product_id'] = record.id
            rec['company_id'] = record.company_id.id
            rec['order_id'] = refund
            rec['qty'] = -product.qty if product else 1
            rec['discount'] = product.discount if product else 0
            rec['price_unit'] = product.price_unit if product else record.list_price
            pos_line.create(cr, uid, rec)
            dat = obj.browse(cr, uid, refund)
            dat.write({'date_order': datetime.datetime.today()})

        abs = {
            'name': _('Return Products'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pos.order',
            'res_id': refund,
            'view_id': False,
            'context': context,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
        }
        return abs
