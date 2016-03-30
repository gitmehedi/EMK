from openerp import api, fields, models
import re

class InheritedResUsers(models.Model):
	_inherit = 'res.users'

	merchandiser = fields.Boolean(string='Merchandiser', store=True, 
								compute="_set_merchandiser_user")
	
	@api.multi
	@api.depends('groups_id')
	def _set_merchandiser_user(self):
		grp_pool = self.env['res.groups']
		grp_ids = grp_pool.search([('name','=','Merchandising User')])
		user_ids = []
		for u in grp_ids.users:
			user_ids.append(u.id)
		for record in self:
			if record.id in user_ids:
				record.merchandiser = True
			else:
				record.merchandiser = False
