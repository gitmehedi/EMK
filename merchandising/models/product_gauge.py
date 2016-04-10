from openerp import api, fields, models
import re

class ProductGauge(models.Model):
	_name = 'product.gauge'
	
	name = fields.Char(string='Name', size=30, required=True)


	
	def create(self, cr, uid, vals, context=None):
		name_value = vals.get('name', False)
		if name_value:
			vals['name'] = name_value.strip()
		return super(ProductGauge, self).create(cr, uid, vals, context=context)
	
	def write(self, cr, uid, ids, vals, context=None):
		name_value = vals.get('name', False)
		if name_value:
			vals['name'] = name_value.strip()
		return super(ProductGauge, self).write(cr, uid, ids, vals, context=context)