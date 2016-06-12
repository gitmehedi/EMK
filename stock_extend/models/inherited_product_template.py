from openerp import api, fields, models
from openerp.exceptions import UserError

class InheritedProductTemplate(models.Model):
	_inherit = 'product.template'
	
	
	@api.multi
	def write(self, vals):
		print "self", self.id
		print "vals", vals
		confirmation = self.action_unit_change()
		return confirmation
		if 'uom_id' in vals:
			new_uom = self.env['product.uom'].browse(vals['uom_id'])
			old_uom = self.uom_id
			if old_uom != new_uom:
				cal_factor = self._unit_conversion(old_uom, new_uom)

			quant_obj = self.env['stock.quant']
			product_obj = self.env['product.product']
			product_record = product_obj.search([('product_tmpl_id', '=', self.id)])
			for product_data in product_record: 
				quant_record = quant_obj.search([('product_id', '=', product_data.id)])
				# Stock quant start
				for record_data in quant_record:
					cal_qty = record_data.qty * cal_factor
					cal_cost = record_data.cost * cal_factor

					vals_qty = {
						'qty': cal_qty,
						'cost':cal_cost
# 						'cost': record_data.price_unit,
					}
					quant_record_single = quant_obj.browse(record_data.id)

					update_record = quant_record_single.write(vals_qty)

				# Stock quant end
				
# 			if old_uom != new_uom:
# 				
# 				if self.env['stock.move'].search([('product_id', 'in', [x.id for x in product.product_variant_ids]), ('state', '=', 'done')], limit=1):
# 					raise UserError(_("XXXXXX You can not change the unit of measure of a product that has already been used in a done stock move. If you need to change the unit of measure, you may deactivate this product."))
		return super(InheritedProductTemplate, self).write(vals)
# 		return True

	@api.multi
	def _unit_conversion(self, old_uom, new_uom):
		uom_obj = self.env['product.uom']
		reference_obj = uom_obj.search([('category_id', '=', new_uom.category_id.id), ('uom_type', '=', 'reference')])
		if(reference_obj != old_uom):
			ref_factor = 1 / old_uom.factor
			new_factor = ref_factor * new_uom.factor

		else:
			new_factor = 1 * new_uom.factor

		return new_factor
		
	
	@api.multi    
	def action_unit_change(self):
		return {
		        'name': ('Confirmation'),
		        'view_type': 'form',
		        'view_mode': 'form',
		        'src_model': 'product.template',
		        'res_model': 'confirmation.wizard',
		        'view_id': False,
		        'type': 'ir.actions.act_window',
		        'target':'new',
		    }