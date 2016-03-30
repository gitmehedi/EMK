from openerp import api, exceptions, fields, models
from datetime import date
from openerp.exceptions import Warning

class ProductReturnWizard(models.TransientModel):
	_name = 'product.return.wizard'

	def get_quantity(self):
		req_id = self._context.get('active_id', False)
		req = self.env['stock.receive'].browse(req_id)
		for data in req:
			return data.quantity

	purchase_type = fields.Selection([('grn_type', 'GRN Number'), ('po_type', 'Purchase Order')], 'Purchase Type', required=True)
	order_no = fields.Char(string='No', size=30, required=True)
	stock_picking_id = fields.Many2one('stock.picking', string="Return From")

	
	@api.one
	def action_submit(self, vals):
		print "self", self.order_no
		print "purchase_type", self.purchase_type
		print "vals+++", vals['active_id']
		active_id = vals['active_id']
		
# 		req_obj = self.env['stock.picking'].browse(self._context.get(active_id))
		print "context id", vals
		
		po_pool = self.env['purchase.order']
		picking_pool = self.env['stock.picking']
		mov_obj = self.env['stock.move']
		stock_picking = picking_pool.search([('id', '=', active_id)])
		stock_move_by_picking = mov_obj.search([('picking_id', '=', active_id)])
		
		location_id = stock_picking.picking_type_id.default_location_src_id.id
		location_dest_id = stock_picking.picking_type_id.default_location_dest_id.id
	
		if(self.purchase_type == 'po_type'):
			tr_ids = po_pool.search([('name', '=', self.order_no)])
			
			if not tr_ids:
				raise Warning(_('Product is not available with this purchase order.'))
			for tr_id in tr_ids:
				for line in tr_id.order_line:
					vals = {
	                    'product_id': line.product_id.id,
	                    'product_uom_qty':line.product_qty,
	                    'name':line.name,
	                    'product_uom':line.product_uom.id,
	                    'location_id': location_id,
	                    'location_dest_id': location_dest_id,
	                    'date_expected': date.today(),
	                    'picking_id' : active_id,
	                    }
					print "Json obj ", vals
					mov_obj.create(vals)
			stock_move_by_picking.unlink()
			print "-----------", stock_move_by_picking
			
		else:
			tr_ids = picking_pool.search([('name', '=', self.order_no)])
			if not tr_ids:
				raise Warning(_('Product is not available with this GRN.'))
			
			for tr_id in tr_ids:
				for line in tr_id.move_lines:
					vals = {
	                    'product_id': line.product_id.id,
	                    'product_uom_qty':line.product_qty,
	                    'name':line.name,
	                    'product_uom':line.product_uom.id,
	                    'location_id': location_id,
	                    'location_dest_id': location_dest_id,
	                    'date_expected': date.today(),
	                    'picking_id' : active_id,
	                    }
					print "Json obj ", vals
					mov_obj.create(vals)
			stock_move_by_picking.unlink()
			print "-----------", stock_move_by_picking

		
		return {
		    'type': 'ir.actions.act_window_close',
		}
		

	
	
