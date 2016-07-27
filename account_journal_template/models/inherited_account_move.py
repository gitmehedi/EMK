from openerp import api, fields, models

class InheritedAccountMove(models.Model):
	_inherit = 'account.move'

	@api.multi
	def action_generate_Item(self, vals):
		if self.journal_id:
			journal_map_ids = self.env['map.journal.acc.journal.template'].search([['journal_id','=',self.journal_id.id]])
			acc_move_line_obj = self.env['account.move.line']
			acc_move_obj = acc_move_line_obj.search([['move_id','=',self.id]]).unlink()
			if journal_map_ids:
				for line in journal_map_ids:
					acc_journal_line_obj = self.env['acc.journal.template.line']
					acc_journal_template_ids = acc_journal_line_obj.search([('acc_journal_template_id', '=', line.template_id.id)])
					if acc_journal_template_ids:
						for move_line in acc_journal_template_ids:
					 		vals = {
					 		    'account_id': move_line.account_id.id,
					 		    'name':move_line.name,
					 		    'debit':move_line.debit,
					 		    'credit': move_line.credit,
					 		    'move_id':self.id
					 		    }
					 		acc_move_line_obj.create(vals)

		
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
