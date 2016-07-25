from openerp import api, exceptions, fields, models

class AccJournalTemplateLine(models.Model):
	_name = "acc.journal.template.line"
	_description = 'Account Journal Template Line'
	
	
	acc_journal_template_id = fields.Many2one('acc.journal.template', required=True, string='Account Journal Template')
	name = fields.Char("Template Item", required=True)
	account_id = fields.Many2one('account.account', string='Account')
	debit = fields.Float(digits=(20, 2), string='Debit',  default=0.0)
	credit = fields.Float(digits=(20, 2), string='Credit', default=0.0)
	
