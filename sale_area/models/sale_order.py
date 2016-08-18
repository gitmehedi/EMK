from openerp.osv import osv, fields

class sale_order(osv.osv):
    '''
    Sale Order
    '''
    _inherit = 'sale.order'    

    _columns = {
        'area_id': fields.many2one('sale.area','Sales Area', select=True),
    }

    def _get_default_sale_area(self, cr, uid, ids, context=None):
        user_pool = self.pool.get('res.users')
        user = user_pool.browse(cr, uid, uid, context=context)
        if user and user.area_id:
            return user.area_id.id
        else:
            return False

    _defaults = {
        'area_id': _get_default_sale_area,
    }

sale_order()