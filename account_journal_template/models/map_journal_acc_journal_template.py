from openerp import api, fields, models

class MapJournalAccJournalTemplate(models.Model):
	_name = "map.journal.acc.journal.template"
	_description = 'Mapping Journal Account & Account Journal Template'
	
	
	journal_id = fields.Many2one('account.journal', required=True, string='Journal Account')
	template_id = fields.Many2one('acc.journal.template', required=True, string='Account Journal Template')
	active = fields.Boolean(default=False)
