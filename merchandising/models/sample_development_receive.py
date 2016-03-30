from openerp import api, exceptions, fields, models

class SampleDevelopmentReceive(models.Model):
	_name = 'sample.development.receive'

	sample_dev_rec_date = fields.Date(default=fields.Date.today, string='Receive Date',
									size=30, required=True)

	sample_dev_rec_qty = fields.Float(digits=(5, 2), string='Quantity', required=True)
	uom = fields.Many2one('product.uom', string="UOM", ondelete='set null', required=True)

	
 	sample_requisition_id = fields.Many2one('sample.requisition', string="Sample Requisition Receive")

	
	_sql_constraints = [
	        ('check_quantity', "CHECK(sample_dev_rec_qty > 0.00)", "Quantity must be greater than zero..")
	    ]