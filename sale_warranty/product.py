from openerp.osv import fields, osv

class product_category(osv.osv):
    
    _inherit = 'product.category'
    
    _columns = {
          'warranty_period':fields.float('Warranty Period', required=True),
    }
    
product_category()