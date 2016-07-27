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
				for map in journal_map_ids:
					acc_journal_line_obj = self.env['acc.journal.template.line']
					template_line_ids = acc_journal_line_obj.search([('acc_journal_template_id', '=', map.template_id.id)])
					if template_line_ids:
						print template_line_ids
						for t_line in template_line_ids:
							print "==========================="
							print t_line
					 		vals = {
					 		    'account_id': t_line.account_id.id,
					 		    'name':t_line.acc_journal_template_id.name,
					 		    'debit':t_line.debit,
					 		    'credit': t_line.credit,
					 		    'move_id':self.id
					 		    }
					 		#acc_move_line_obj.create(vals)

		
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
