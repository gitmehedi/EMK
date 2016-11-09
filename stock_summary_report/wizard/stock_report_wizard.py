from openerp import api, exceptions, fields, models
from datetime import date
import time
from openerp.exceptions import Warning
from openerp.tools.translate import _

class StockReportWizard(models.TransientModel):
	_name = 'stock.report.wizard'

	start_date = fields.Date('Start Date', default=fields.Date.today())
	end_date = fields.Date('End Date', default=fields.Date.today())
	warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=True)
	category_id = fields.Many2one('product.category', string='Category', required=False)
	product_id = fields.Many2one('product.product', string='Product', required=False)
	
	
	@api.multi	
	def stock_report(self,data):
		
		return self.env['report'].get_action(self, 'stock_summary_report.report_stock_summary_qweb', data=data)
		