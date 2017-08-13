import time

from openerp.osv import osv, fields
from openerp.tools.translate import _


class PosProductReturn(osv.osv_memory):
    _name = 'pos.product.return'
    _description = 'Point of Sale Product Return'

    _columns = {
        'product_ids': fields.many2many('product.product', string='Products', required=True),
    }

    def return_products(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('pos.order.line')
        records = self.browse(cr, uid, ids, {})
        for record in records.product_ids:
            rec = {}

            # product = line_obj.search(cr, uid,[('product_id','=',record.id),('order_id','=',context['active_id'])])
            product = line_obj.browse(cr, uid, [line_obj.search(cr, uid,[('product_id','=',record.id)])[0]])
            rec['name'] = record.name
            rec['product_id'] = record.id
            rec['company_id'] = record.company_id.id
            rec['qty'] = product.qty if product else 1
            rec['discount'] = product.discount if product else 0
            rec['order_id'] = context['active_id']
            rec['price_unit'] = product.price_unit if product else record.list_price
            line_obj.create(cr, uid, rec)

            # return True
