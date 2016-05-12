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
	
	
	@api.multi
	@api.onchange('picking_type_id')
	def change_picking_type(self):
		res = {}
		if self.picking_type_id:
			print "--pick_type--",self.picking_type_id
			print "--source--",self.picking_type_id.default_location_src_id
			print "--dest--",self.picking_type_id.default_location_dest_id
			print "--location_id--",self.location_id
			print "--location_dest_id--",self.location_dest_id
			location_id = self.picking_type_id.default_location_src_id
			location_dest_id = self.picking_type_id.default_location_dest_id
			res['value'] = {'location_id': location_id,
							'location_dest_id': location_dest_id,}
			print "--res--",res
			return res
			