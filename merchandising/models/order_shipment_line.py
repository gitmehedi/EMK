from openerp import api, fields, models
from openerp.addons.helper import validator

class OrderShipmentLine(models.Model):
	_name = 'order.shipment.line'
	
	name = fields.Char(string='Name', size=30, required=True)
	status = fields.Boolean(string='Status', default=True)


	@api.model
	def create(self, vals):
		vals['name'] = vals.get('name', False).strip()
		return super(OrderShipmentLine, self).create(vals)
	
	@api.multi
	def write(self, vals):
		vals['name'] = vals.get('name', False).strip()
		return super(OrderShipmentLine, self).write(vals)
