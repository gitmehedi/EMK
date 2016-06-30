from openerp.osv import fields, osv

class product_product(osv.osv):
    
    _inherit = 'product.product'
    
    _columns = {
          'gaston_finished_battery':fields.boolean('Gaston Finished Battery',),
        }
    
    _defaults = {
          'gaston_finished_battery':False,
        }
    
product_product()