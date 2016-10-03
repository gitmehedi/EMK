from openerp.osv import fields, osv, orm
from openerp import tools

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    
    _columns = {
        'sale_return': fields.boolean('Sales Return', readonly=True),
    }

stock_picking()