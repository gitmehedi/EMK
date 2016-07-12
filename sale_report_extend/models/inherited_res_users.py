from openerp import api, fields, models
from openerp.osv import osv

class InheritedResUsers(models.Model):
	_inherit = 'res.users'

	target_amount = fields.Float(string='Sell Target', digits=(15, 2))

