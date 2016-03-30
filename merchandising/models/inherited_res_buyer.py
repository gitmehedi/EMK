from openerp import api, fields, models
from openerp.osv import osv
import validators
from openerp.addons.helper import validator
import re

class InheritedResBuyer(models.Model):
	_inherit = 'res.partner'

	name = fields.Char(string='Name', size=30, required=True)
	street = fields.Char(string='Street', size=30)
	street2 = fields.Char(string='Street2', size=30)
	dept_ids = fields.Many2many(comodel_name='merchandising.dept',
                          relation='merchandising_dept_relation',
                          column1='partner_id',
                          column2='merchandising_dept_id')
	
	season_ids = fields.Many2many(comodel_name='res.season',
                          relation='season_partner_rel',
                          column1='partner_id',
                          column2='season_id')
	courier = fields.Boolean(string='Courier', default=False)
	state_visible = fields.Boolean(string='State Required', default=False)
	
	# One2many Relationship
	styles_ids = fields.One2many('product.style', 'buyer_id')

	@api.multi
	def _check_illegal_char(self, value):
		values = {}
		if(value.get('name', False)):
			values['Name'] = (value.get('name', False))
# 		if(value.get('street', False)):
# 			values['street'] = (value.get('street', False))
		check_space = validator._check_space(self, values, validator.msg)
		check_special_char = validator._check_special_char(self, values, validator.msg)
		validator.generate_validation_msg(check_space, check_special_char)
		return True
	
	@api.multi
	def _validate_email(self):
	    for partner in self:
	    	if partner.email:
		        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", partner.email) == None:
		            return False
	    return True
	   
	@api.multi
	def _validate_domain(self):
		if self.website:
			if validators.url(self.website):
				return True
		else:
			return True
		
		return False
	
	_constraints = [
#         (_check_illegal_char, 'Please remove only space or special character.', ['name']),
        (_validate_email, 'Please enter a valid email address.', ['email']),
        (_validate_domain, 'Please enter a valid domain URL.', ['website'])
    ]

	@api.model
	def create(self, vals):
		self._check_illegal_char(vals)
		name_value = vals.get('name', False)
		if name_value:
			vals['name'] = name_value.strip()
		return super(InheritedResBuyer, self).create(vals)
	
	@api.multi
	def write(self, vals):
		self._check_illegal_char(vals)		
		name_value = vals.get('name', False)		
		if name_value:
			vals['name'] = name_value.strip()
		return super(InheritedResBuyer, self).write(vals)
	
	@api.onchange('country_id')
	def onchange_country(self):
		if self.country_id and self.country_id.state_required:
			self.state_visible = True
		else:
			self.state_visible = False
