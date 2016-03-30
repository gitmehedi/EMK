from openerp import api, exceptions, fields, models

class SampleDevelopmentRequest(models.Model):
	_name = 'sample.development.request'

	def _get_requisition(self):
		return self.env['sample.requisition'].browse(self._context.get('active_id'))

	sample_dev_req_date = fields.Date(default=fields.Date.today, string='Request Date',
									size=30, required=True)
# 	sample_dev_req_by = fields.Many2one('res.users', string="Request By",
# 									ondelete='set null', required=True)
	sample_dev_req_qty = fields.Float(digits=(5, 2), string='Quantity', required=True)
	uom = fields.Many2one('product.uom', string="UOM", ondelete='set null', required=True)
	
	sample_requisition_id = fields.Many2one('sample.requisition', string="Sample Requisition")
# 	, default=_get_requisition
	
	_sql_constraints = [
        ('check_quantity', "CHECK(sample_dev_req_qty > 0.00)", "Quantity must be greater than zero..")
    ]
	
