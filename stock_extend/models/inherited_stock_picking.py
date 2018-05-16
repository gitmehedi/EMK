from openerp import api, fields, models


class InheritedStockPicking(models.Model):
	_inherit = 'stock.picking'


	return_type = fields.Boolean(string='Return Type', default=False)
	stock_issue = fields.Boolean(string='Stock Issue', default=False)
	stock_return = fields.Boolean(string='Stock Return', default=False)
	stock_transfer = fields.Boolean(string='Stock Transfer', default=False)
	picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type', 
						states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
						required=True)
	
	@api.model
	def create(self, values):
		picking = super(InheritedStockPicking, self).create(values)
		if picking and picking.stock_issue or picking.stock_transfer and picking.move_lines:
			picking.move_lines.write({'state':'assigned'})
			picking.write({'state':'assigned'})
		return picking
	

