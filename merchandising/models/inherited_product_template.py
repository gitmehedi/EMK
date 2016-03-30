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
