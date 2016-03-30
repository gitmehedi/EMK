from openerp import api, fields, models
import re

class ResShippingCourier(models.Model):
	_name = 'res.shipping.courier'
	
	name = fields.Char(string='Name', size=30, required=True)
	branch = fields.Char(string='branch', size=50)
	contact_number = fields.Char(string='Contact Number', size=30, required=True)
	address = fields.Text(string='Address')
	
	@api.multi
	def _check_special_char(self):
		for courier in self:
			if re.search("[^A-Za-z0-9 ]",courier.name)==None:
				return True
		return False
	
	_constraints = [
        (_check_special_char, 'Please remove special character.', ['name'])
    ]
	
	def create(self, cr, uid, vals, context=None):
		name_value = vals.get('name', False)
		if name_value:
			vals['name'] = name_value.strip()
		return super(ResShippingCourier, self).create(cr, uid, vals, context=context)
	
	def write(self, cr, uid, ids, vals, context=None):
		name_value = vals.get('name', False)
		if name_value:
			vals['name'] = name_value.strip()
		return super(ResShippingCourier, self).write(cr, uid, ids, vals, context=context)