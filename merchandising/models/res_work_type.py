from openerp import api, fields, models
from openerp.addons.helper import validator
from openerp.osv import osv
import validators
import re

class ResWorkType(models.Model):
	_name = 'res.work.type'
	
	name = fields.Char(string='Name', size=30, required=True)
	
	@api.multi
	def _check_illegal_char(self, value):
		values = {}
		if(value.get('name', False)):
			values['Name'] = (value.get('name', False))
			
		check_space = validator._check_space(self, values, validator.msg)
		check_special_char = validator._check_special_char(self, values, validator.msg)
		validator.generate_validation_msg(check_space, check_special_char)
		return True
   
	@api.multi
	def check_duplicate(self, value):
		records = self.search_read([],['name'])
		check_val = {}
		field_val = ''
		field_name = ''
		if(value.get('name', False)):
			check_val['name'] = (value.get('name', False))
		for  value in check_val:
			field_val =  check_val[value]
			field_name =  value
		if field_name != "" and   field_val != "":
			check_duplicate = validator._check_duplicate_data(self, field_val, field_name, records, validator.msg)
			validator.generate_validation_msg(check_duplicate, "")
		return True
	
	
	_sql_constraints = [
		('_check_season_name_uniq', 'unique(name)', "Name already exists!"),
	]
	
	@api.model
	def create(self, vals):
		self._check_illegal_char(vals)
		self.check_duplicate(vals)
		name_value = vals.get('name', False)
		if name_value:
			vals['name'] = name_value.strip()
		return super(ResWorkType, self).create(vals)
	
	@api.multi
	def write(self, vals):
		self._check_illegal_char(vals)
		self.check_duplicate(vals)
		name_value = vals.get('name', False)
		if name_value:
			vals['name'] = name_value.strip()
		return super(ResWorkType, self).write(vals)