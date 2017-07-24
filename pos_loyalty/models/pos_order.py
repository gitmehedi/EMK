from openerp.osv import fields, osv


class PosOrder(osv.osv):
    _inherit = 'pos.order'

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = super(PosOrder, self)._amount_all(cr, uid, ids, name, args, context)

        return res