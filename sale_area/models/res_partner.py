from openerp.osv import fields, osv

class res_partner(osv.osv):
    
    _inherit = 'res.partner'
    
    _columns = {
          'area_id': fields.many2one("sale.area", 'Area'),
        }
    
res_partner()
