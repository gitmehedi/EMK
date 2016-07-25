from openerp import api, exceptions, fields, models

class AccJournalTemplate(models.Model):
	_name = "acc.journal.template"
	_description = 'Account Journal Template'
	
	name = fields.Char("Template", required=True,readonly=True, states={'draft': [('readonly', False)]})
	active = fields.Boolean(default=False)
	line_ids = fields.One2many('acc.journal.template.line', 'acc_journal_template_id', string='Template Line', readonly=True, states={'draft': [('readonly', False)]})
	state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),('approve', 'Approve'),('cancel', 'Cancel')], default="draft", readonly=True, states={'draft':[('readonly', False)]})
	
	@api.multi
	def action_confirm(self):
		self.state = "confirm"
	
	@api.multi
	def action_approve(self):
		self.state = "approve"