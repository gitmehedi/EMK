from openerp import api, fields, models

class InheritedStockPickingType(models.Model):
	_inherit = 'stock.picking.type'

	stock_issue_flag = fields.Boolean(default=False)
	stock_return_flag = fields.Boolean(default=False)
	stock_transfer_flag = fields.Boolean(default=False)
