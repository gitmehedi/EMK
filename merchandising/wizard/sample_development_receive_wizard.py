from openerp import api, exceptions, fields, models

class SampleDevelopmentReceiveWizard(models.TransientModel):
	_name = 'sample.development.receive.wizard'

	def get_quantity(self):
		req_id = self._context.get('active_id', False)
		req = self.env['sample.requisition'].browse(req_id)
		for data in req:
			return data.quantity

	
	def get_uom(self):
		req_id = self._context.get('active_id', False)
		req = self.env['sample.requisition'].browse(req_id)
		for data in req:
			return data.uom
		
	sample_dev_rec_date = fields.Date(default=fields.Date.today, string='Receive Date',
									size=30, required=True)

	sample_dev_rec_qty = fields.Float(digits=(5, 2), string='Quantity',
									required=True, default=get_quantity)
	uom = fields.Many2one('product.uom', string="UOM", ondelete='set null', readonly=True, default=get_uom)


	
	def action_submit(self, cr, uid, ids, context=None):
		print context
		req_obj = self.pool.get('sample.requisition')
		dev_obj = self.pool.get('sample.development.receive')
		req_id = context.get('active_id', False)
		req = req_obj.browse(cr, uid, req_id, context=context)
		for data_uom in req:
			parent_uom = data_uom.uom
			
		for data in self.browse(cr, uid, ids):
		    vals = {
		            'sample_dev_rec_date': data.sample_dev_rec_date,
 		         	'sample_requisition_id':req_id,
 		         	'sample_dev_rec_qty':data.sample_dev_rec_qty,
		          	'uom':parent_uom.id
		            }
		res = dev_obj.create(cr, uid, vals, context=context)

		req_obj.write(cr, uid, [req_id], {'state':'received'}, context=context)
		
		return {
		    'type': 'ir.actions.act_window_close',
		}
		
	
	
