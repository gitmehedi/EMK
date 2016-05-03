from openerp import api, fields, models


class InheritedBuyerWorkOrder(models.Model):
	_inherit = 'sale.order'

	
	@api.multi    
	def action_confirm(self):
		res = {
			'code': self.hs_code,
			'currency_id': self.currency_id.id,
			'start_date':self.epo_date,
			'state':'open',
			'name':self.name
			}
		analytic_acc_obj = self.env['account.analytic.account']
		result = analytic_acc_obj.create(res)
		return super(InheritedBuyerWorkOrder, self).action_confirm()
