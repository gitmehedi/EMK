from openerp import api, fields, models


class InheritedStockPicking(models.Model):
	_inherit = 'stock.picking'

	stock_reservation_id = fields.Many2one('stock.reservation', 'Reservation')
	stock_deallocation_id = fields.Many2one('stock.reservation', 'De-Allocation')
	stock_reallocation_id = fields.Many2one('stock.reservation', 'Re-Allocation')
