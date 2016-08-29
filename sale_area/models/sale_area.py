from openerp.osv import fields, osv
from openerp import api, tools, SUPERUSER_ID

class sale_area(osv.osv):
    
    # @api.multi
    # def name_get(self):
    #     def get_names(cat):
    #         """ Return the list [cat.name, cat.parent_id.name, ...] """
    #         res = []
    #         while cat:
    #             res.append(cat.name)
    #             cat = cat.parent_id
    #         return res
    #
    #     return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]
    #
    # def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
    #     res = self.name_get(cr, uid, ids, context=context)
    #     return dict(res)
    
    _name = 'sale.area'
    
    _columns = {
        'name': fields.char('Area Name', required=True, select=True),
        'complete_name': fields.char('Area Name', select=True),
        'parent_id': fields.many2one('sale.area','Parent Area', select=True, ondelete='cascade'),
        'child_id': fields.one2many('sale.area', 'parent_id', string='Child Areas'),
        'code':fields.char('Code'),
        'manager_id':fields.many2one('res.users', 'Manager', required=True ),
        'warehouse_id':fields.many2one('stock.warehouse', 'Warehouse', required=True ),
        }
    
    _order = 'name'

    """All function which process data and operation"""

    @api.model
    def create(self, vals):
        vals['complete_name'] = 'Bangladesh Complete Name'

        return super(sale_area, self).create(vals)
    
sale_area()

