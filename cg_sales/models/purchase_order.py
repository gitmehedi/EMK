from openerp.osv import osv
from openerp import api, fields, models

class purchaseorderline(models.Model):
    _inherit = 'purchase.order.line'
    
    remark = fields.Char( string='Remarks')