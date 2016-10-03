from openerp import models, fields

class stock_picking(models.Model):
    _inherit = "stock.picking"
    
    courier_id = fields.Many2one(
        'delivery.courier',
        string='Transport',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})