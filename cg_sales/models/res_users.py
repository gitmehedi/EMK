from openerp.osv import osv
from openerp import api, fields, models

class resusers(models.Model):
    _inherit = 'res.users'
    
    area_id = fields.Many2one("sale.area", string='Sales Area')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    
