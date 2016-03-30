from openerp import api, fields, models
from openerp.addons.helper import validator

class DeliveryTerm(models.Model):
	_name = 'delivery.term'
	
	name = fields.Char(string='Name', size=30, required=True)
	status = fields.Boolean(string='Status', default=True)
	
	@api.multi
	def _validate_data(self, value):
		msg , filterChar = {}, {}
		
		filterChar['Name'] = value.get('name', False)
		
		msg.update(validator._validate_character(filterChar, True))
		validator.validation_msg(msg)
		
		return True
	
	@api.model
	def create(self, vals):
		self._validate_data(vals)
		vals['name'] = vals.get('name', False).strip()
		return super(DeliveryTerm, self).create(vals)
	
	@api.multi
	def write(self, vals):
		self._validate_data(vals)
		if vals.get('name', False):
			vals['name'] = vals.get('name', False).strip()
		return super(DeliveryTerm, self).write(vals)
