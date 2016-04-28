from openerp import models, fields, api
from openerp.addons.helper import validator

class ReservationQuant(models.Model):
    _name = 'reservation.quant'
    _description = 'Reservation Quant'
    
    
    product_id = fields.Many2one('product.product', string="Product")
    reserve_quantity = fields.Float(digits=(20, 2), string='Reserve Quantity', required=True, default=0.0)
    uom = fields.Many2one('product.uom', string="UOM")
    location = fields.Many2one('stock.location', 'Location',required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',required=True)