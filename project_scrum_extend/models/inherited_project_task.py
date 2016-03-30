from openerp import api, fields, models
import re

class InheritedProjectTask(models.Model):
	_inherit = 'project.task'


	@api.model
	def create(self, values):
		task = super(InheritedProjectTask, self).create(values)
		task_state = 1
		for t in task.us_id.task_ids:
			if t.kanban_state != 'done':
				task_state = 0
				t.us_id.story_state = 'in progress'	
				return task			
			else:
				task_state = 1
				t.us_id.story_state = 'done'
		return task
	
	@api.multi
	def write(self, vals):
		task = super(InheritedProjectTask, self).write(vals)		
		task_state = 1	
		for t in self.us_id.task_ids:
			if t.kanban_state != 'done':
				task_state = 0
				t.us_id.story_state = 'in progress'	
				return task			
			else:
				task_state = 1
				t.us_id.story_state = 'done'
				
		return task
	
	
