from openerp import api, fields, models

class InheritedProductTemplate(models.Model):
	"""
	Inherit Product Templates models and add three attribute yarn, accessories and finish goods
	for merchandising process calculation
	"""
	_inherit = 'product.template'

	yarn = fields.Boolean(string="Yarn", default=False)
	accessories = fields.Boolean(string="Accessories", default=False)
	finish_goods = fields.Boolean(string="Finish Goods", default=False)
	standard_wage  = fields.Float(string="Standard Wage ",digits=(15, 2))
	productivity = fields.Float(string="Productivity",digits=(15, 2))
	costing_type = fields.Selection([('pcs','Pcs'),('dzn','Dzn')], default='pcs',string="Costing Type")
