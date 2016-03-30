from openerp import api, fields, models
import re

class InheritedUserStory(models.Model):
	_inherit = 'project.scrum.us'

	story_state = fields.Selection([('draft', 'Draft'), ('in progress', 'In Progress'), ('done', 'Done')], default="draft", string='State', required=False)

	@api.one
	def action_draft(self):
		self.state = 'draft'

	@api.one
	def action_in_progress(self):
		self.state = 'in progress'
	
	@api.one
	def action_done(self):
		self.state = 'done'
