from openerp.osv import fields, osv
# from openerp import api, fields, models
from openerp import tools
from datetime import datetime

class StockInventory(osv.osv):
    
    _name = 'stock.inventory.report'
    _auto = False
    
    _columns = {
        'id': fields.integer('Sequence'),
        'name': fields.char('Product'),
        'code': fields.char('Code'),
        'qty_dk': fields.float('Opening Stock'),
        'qty_in_tk': fields.float('Stock In'),
        'qty_out_tk': fields.float('Stock Out'),
        'qty_ck': fields.float('Closing Stock'),
    }
    
    
StockInventory()