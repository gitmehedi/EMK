from openerp import api, fields, models
from openerp.addons.helper import validator

class OrderShipmentLine(models.Model):
	_name = 'order.shipment.line'
	
	name = fields.Char(string='Name', size=30, required=True)
	status = fields.Boolean(string='Status', default=True)
	
	
	@api.multi
	def _check_special_char(self):
		for term in self:
			if re.search("[^A-Za-z0-9 ]", term.name) == None:
				return True
		return False
	
	_constraints = [
        (_check_special_char, 'Please remove special character.', ['name'])
    ]
	
	@api.model
	def create(self, vals):
		vals['name'] = vals.get('name', False).strip()
		return super(DeliveryTerm, self).create(vals)
	
	@api.multi
	def write(self, vals):
		vals['name'] = vals.get('name', False).strip()
		return super(DeliveryTerm, self).write(vals)
