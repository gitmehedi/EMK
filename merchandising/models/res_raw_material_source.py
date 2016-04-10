from openerp import api, fields, models
import re

class ResRawMaterialSource(models.Model):
	_name = 'res.raw.material.source'
	
	name = fields.Char(string='Name', size=30, required=True)
	

	def create(self, cr, uid, vals, context=None):
		name_value = vals.get('name', False)
		if name_value:
			vals['name'] = name_value.strip()
		return super(ResRawMaterialSource, self).create(cr, uid, vals, context=context)
	
	def write(self, cr, uid, ids, vals, context=None):
		name_value = vals.get('name', False)
		if name_value:
			vals['name'] = name_value.strip()
		return super(ResRawMaterialSource, self).write(cr, uid, ids, vals, context=context)
