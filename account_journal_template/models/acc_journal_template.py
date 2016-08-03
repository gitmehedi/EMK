from openerp import api, exceptions, fields, models
from openerp.addons.helper import validator

class AccJournalTemplate(models.Model):
	_name = "acc.journal.template"
	_description = 'Account Journal Template'
	
	name = fields.Char("Template", required=True)
	active = fields.Boolean(default=True)
	line_ids = fields.One2many('acc.journal.template.line', 'acc_journal_template_id', string='Template Line')

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
	    ('_check_name_uniq', 'unique(name)', "Name already exists!"),
	]
	
	@api.model
	def create(self, vals):
	    self.check_duplicate(vals)
	    name_value = vals.get('name', False)
	    if name_value:
	        vals['name'] = name_value.strip()
	    return super(AccJournalTemplate, self).create(vals)
	
	@api.multi
	def write(self, vals):
	    self.check_duplicate(vals)
	    name_value = vals.get('name', False)
	    if name_value:
	        vals['name'] = name_value.strip()
	    return super(AccJournalTemplate, self).write(vals)
	
	@api.multi
	def copy(self, vals):
		name_vale=('Copy' or '')+' '+(self.name or '')
		if self.name:
			vals['name'] = name_vale
		return super(AccJournalTemplate, self).copy(vals)