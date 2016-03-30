from openerp import api, fields, models
import re

class ProjectScrumTestData(models.Model):
	_name = 'project.scrum.test.data'

	pre_condition = fields.Char(string='Pre Condition',size=30)
	name = fields.Text(string='Description')
	expected_result = fields.Text(string='Expected Result')
	actual_result = fields.Text(string='Actual Result')
	project_scrum_test_data_id = fields.Many2one('project.scrum.test', string="Description Info")
