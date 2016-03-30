from openerp import api, fields, models

class InheritedWarehouse(models.Model):
	_inherit = 'stock.warehouse'

	wh_stock_ana_resv_id= fields.Many2one('stock.location', 'Stock Analytic Reservation Location')
