from openerp import api, exceptions, fields, models
from openerp.exceptions import Warning
from datetime import date

class AccJounalTemplateWizard(models.TransientModel):
	_name = 'acc.journal.template.wizard'

	acc_journal_template_ids = fields.Many2many('acc.journal.template', string="Account Journal Template", required=True)

	
	@api.one
	def action_generate_joural_acc(self, vals):
 
		active_id = vals['active_id']
		acc_move_obj = self.env['account.move']
		
		acc_move = acc_move_obj.search([('id', '=', active_id)])

		acc_move_line_obj = self.env['account.move.line']
		acc_move_obj = acc_move_line_obj.search([['move_id','=',acc_move.id]]).unlink()
		
		if self.acc_journal_template_ids:
			for line in self.acc_journal_template_ids:
				acc_journal_line_obj = self.env['acc.journal.template.line']
				acc_journal_line_ids = acc_journal_line_obj.search([('acc_journal_template_id', '=', line.id)])
				
				if acc_journal_line_ids:
					for move_line in acc_journal_line_ids:
				 		vals = {
				 		    'account_id': move_line.account_id.id,
				 		    'name':move_line.name,
				 		    'debit':move_line.debit,
				 		    'credit': move_line.credit,
				 		    'move_id':acc_move.id
				 		    }
				 		acc_move_line_obj.create(vals)
				 		
		return {
		    'type': 'ir.actions.act_window_close',
		}
 		

	
	
