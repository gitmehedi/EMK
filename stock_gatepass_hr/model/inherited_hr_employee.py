from openerp import api, fields, models


class InheritedHrEmployee(models.Model):
	_inherit = 'hr.employee'
	
	security_guard = fields.Boolean("Security Guard", default=False)
	