from openerp import api, fields, models
import re

class InheritedResCountry(models.Model):
	_inherit = 'res.country'

	state_required = fields.Boolean(string='State Required', default=False)
