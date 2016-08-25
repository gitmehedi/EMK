from openerp import api, exceptions, fields, models
from datetime import date
import time
from openerp.exceptions import Warning
from openerp.tools.translate import _

class PettyCashReportWizard(models.TransientModel):
	_name = 'petty.cash.report.wizard'

	start_date = fields.Date('Start Date', default=fields.Date.today())
	end_date = fields.Date('End Date', default=fields.Date.today())
	_sql_constraints = [
        ('_check_date_comparison', "CHECK ( (start_date <= end_date))", "The Start date must be lower than End date.")
    ]
	
	@api.multi	
	def petty_cash_report(self,data):
		acc_ids = []
		dict = {}
		obj_acc = self.env['petty.cash.disbursement']
		obj_acc_ids = obj_acc.search([('create_date','>=',self.start_date),('create_date','<=',self.end_date)])
		for acc_id in obj_acc_ids:
			acc_ids.append(acc_id.id)
 
		data['ids'] = acc_ids 
		data['form1'] = self.read([], ['start_date', 'end_date'])[0]
		return self.env['report'].get_action(self, 'petty_cash_register.report_petty_cash_qweb', data=data)
		