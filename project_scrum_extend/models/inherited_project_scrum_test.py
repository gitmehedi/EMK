from openerp import api, fields, models
import re

class InheritedProjectScrumTest(models.Model):
	_inherit = 'project.scrum.test'

	description_test = fields.Text(string='Test Data')
	stats_test = fields.Selection([('draft', 'Draft'), ('in progress', 'In Progress'), ('cancel', 'Cancelled'), ('done', 'Completed')], default="draft", string='State', required=False)
	test_data_ids = fields.One2many('project.scrum.test.data','project_scrum_test_data_id',string="Test Data")
	
