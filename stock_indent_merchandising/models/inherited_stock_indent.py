from openerp import api, fields, models

class InheritedStockIndent(models.Model):
	_inherit = 'indent.indent'
	
	analytic_account_id = fields.Many2one('account.analytic.account', 'EPO No',readonly=True, states={'draft': [('readonly', False)]})
	type =  fields.Selection([('gen', 'General Item'), ('bom', 'BOM Item')], 'Type', required=True, readonly=True, states={'draft': [('readonly', False)]})
	bom_flag = fields.Boolean(default=False)

	
	@api.onchange('type')
	def onchnage_bom_item(self):
		print 'type ',self.type
		if self.type == "bom":
		   self.bom_flag = True
		else:
			self.bom_flag = False
	
class InheritedIndentProductLines(models.Model):
	_inherit = 'indent.product.lines'	
	
	def _get_indent_type_bom_flag_value(self):
		print '---indent type--',self._context.get('indent_type', False)
		if self._context.get('indent_type', False) == "bom":
		    return True
		else:
		    return False

	indent_type_bom_flag = fields.Boolean(default=_get_indent_type_bom_flag_value)