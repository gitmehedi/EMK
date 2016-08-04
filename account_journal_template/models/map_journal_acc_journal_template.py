from openerp import api, exceptions, fields, models
from openerp.exceptions import ValidationError

class MapJournalAccJournalTemplate(models.Model):
	_name = "map.journal.acc.journal.template"
	_description = 'Mapping Journal Account & Account Journal Template'
	
	
	journal_id = fields.Many2one('account.journal', required=True, string='Journal')
	template_id = fields.Many2one('acc.journal.template', required=True, string='Journal Template')
	active = fields.Boolean(default=True)
	_rec_name= "id"

	_sql_constraints = [
        ('charges_key_unique', 'unique (journal_id, template_id)', 'This record is already exists.')
    ]