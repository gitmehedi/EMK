from openerp import api, fields, models

class InheritedProductTemplate(models.Model):
	_inherit = 'product.template'
	
	bom_item = fields.Boolean("Can be as BOM item", default=False)
	

	
	@api.onchange('general_item')
	def onchnage_gen_item(self):
		print 'general_item ',self.general_item
		print 'bom_item ', self.bom_item
		if (self.general_item == True) or (self.bom_item == True):
		   self.gen_bom_flag = True
		else:
		 self.gen_bom_flag = False
	
	@api.onchange('bom_item')
	def onchnage_bom_item(self):
		print 'bom_item ',self.bom_item
		print 'general_item ',self.general_item
		if (self.bom_item == True) or (self.general_item == True):
			self.gen_bom_flag = True
		else:
			self.gen_bom_flag = False