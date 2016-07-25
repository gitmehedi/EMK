from openerp import api, fields, models

class InheritedAccountMove(models.Model):
	_inherit = 'account.move'

	@api.multi    
	def action_wizard_open(self, context=None):
		return {
		        'name': ('Select Account Journal Template'),
		        'view_type': 'form',
		        'view_mode': 'form',
		        'src_model': 'account.move',
		        'res_model': 'acc.journal.template.wizard',
		        'view_id': False,
		        'type': 'ir.actions.act_window',
		        'target':'new',
		        'context':context
		    }
