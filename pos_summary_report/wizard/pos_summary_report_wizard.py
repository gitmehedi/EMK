from openerp import api, exceptions, fields, models


class PosSummaryReportWizard(models.TransientModel):
	_name = 'pos.summary.report.wizard'

	start_date = fields.Date('Start Date', default=fields.Date.today(), required=True)
	end_date = fields.Date('End Date', default=fields.Date.today())
	point_of_sale_id = fields.Many2one('pos.config', string='Point Of Sale', required=True)

	@api.multi	
	def pos_order_report(self,data):
		return self.env['report'].get_action(self, 'report_pos_order_summary.report_pos_summary_qweb', data=data)
		