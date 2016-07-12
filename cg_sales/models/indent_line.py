from openerp.osv import osv, fields
import time

class indent_product_lines(osv.osv):
    
    _inherit = 'indent.product.lines'   

    _columns = {
        'remark':fields.char('Remarks'),
    }
    
    
            
indent_product_lines()