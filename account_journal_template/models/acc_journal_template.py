from openerp import api, fields, models

class AccJournalTemplate(models.Model):
	_name = "acc.journal.template"
	_description = 'Account Journal Template'
	
	name = fields.Char("Template", required=True)
	active = fields.Boolean(default=False)
	line_ids = fields.One2many('acc.journal.template.line', 'acc_journal_template_id', string='Template Line')
