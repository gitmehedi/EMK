import time
import datetime

from openerp import api
from openerp.osv import osv, fields
from openerp.tools.translate import _


class PosProductReturn(osv.osv_memory):
    _name = 'pos.product.return'
    _description = 'Point of Sale Product Return'

    _columns = {
        'product_ids': fields.many2many('product.product', string='Products', required=True),
    }

    def return_products(self, cr, uid, ids, context=None):
        ins = self.pool.get('pos.order')
        ins_line = self.pool.get('pos.order.line')
        refund = ins.refund(cr, uid, context['active_id'])

        pos_ids = ins.search(cr, uid, [('id', '=', context['active_id'])])
        pos_rec = ins.browse(cr, uid, pos_ids)
        records = self.browse(cr, uid, ids, {})

        for record in records.product_ids:
            ids = ins_line.search(cr, uid, [('order_id', '=', context['active_id']), ('product_id', '=', record.id)])
            ids = ids[0] if ids else []
            product = ins_line.browse(cr, uid, ids)
            rec = {}
            rec['name'] = record.name
            rec['product_id'] = record.id
            rec['company_id'] = record.company_id.id
            rec['order_id'] = refund
            rec['qty'] = -product.qty if product else 1
            rec['discount'] = self.get_discount_price(pos_rec, record)
            rec['price_unit'] = product.price_unit if product else record.list_price
            ins_line.create(cr, uid, rec)
            dat = ins.browse(cr, uid, refund)
            dat.write({'date_order': datetime.datetime.today()})

        return {
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

    def get_discount_price(self, ins, record):
        for rec in ins.lines:
            if rec.product_id.product_tmpl_id.id == record.product_tmpl_id.id:
                return rec.discount

