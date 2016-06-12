from openerp import api, fields, models
from openerp import _
from openerp.exceptions import Warning

class InheritedPurchaseRequisition(models.Model):
	_inherit = 'purchase.requisition'

	bom_id = fields.Many2one('bom.consumption', string="Bill of Material", readonly=True, states={'draft': [('readonly', False)]})
	bom_flag = fields.Boolean(default=False)
	bom_flag1 = fields.Boolean(default=False)
	
	
	@api.multi
	@api.onchange('line_ids')
	def _onchange_type(self, context=None):
		if self.bom_id and self.line_ids:
			self.bom_flag1 = True
	
	@api.multi
	@api.onchange('bom_id')
	def change_bom(self):
		if self.bom_id:
			self.bom_flag = True

	@api.multi
	def action_wizard(self, context=None):
		return {
                'name': ('Confirmation'),
                'view_type': 'form',
                'view_mode': 'form',
                'src_model': 'purchase.requisition',
                'res_model': 'confirmation.wizard.pr',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target':'new',
            }
	
	@api.multi
	def sent_suppliers(self):
		if self.bom_id and self.line_ids:
			pro_qty = []
			prod_id = []
			bom_li_id = []
			
			for line in self.line_ids:
				prod_id.append(line.product_id.id)
				bom_li_id.append(line.bom_line_id.id)
				pro_qty.append(line.product_qty)
			
			obj_bom_line = self.env['bom.consumption.line']
				
			bom_line_id = obj_bom_line.search(['&',['id','in',bom_li_id],'&',['product_id','in',prod_id],'|',['mc_yarn_id','=',self.bom_id.id],['mc_acc_id','=',self.bom_id.id]])
 			
			i=0;
			for line in bom_line_id:
				updated_qty = 0;
				if pro_qty[i]:
					updated_qty = pro_qty[i]
				res = {
						'p_r_p_qty':line.p_r_p_qty+updated_qty
					}
				i=i+1
				if line.p_r_p_qty+updated_qty > line.quantity:    
					raise Warning(_('Quantity can not be greater than BOM Line Quantity.'))
				else:
					line.write(res)
		self.state = "in_progress"			
	
	@api.multi
	def tender_reset(self):
		if self.bom_id and self.line_ids:
			pro_qty = []
			prod_id = []
			bom_li_id = []
			
			for line in self.line_ids:
				prod_id.append(line.product_id.id)
				bom_li_id.append(line.bom_line_id.id)
				pro_qty.append(line.product_qty)
				
			obj_bom_line = self.env['bom.consumption.line']
				
			bom_line_id = obj_bom_line.search(['&',['id','in',bom_li_id],'&',['product_id','in',prod_id],'|',['mc_yarn_id','=',self.bom_id.id],['mc_acc_id','=',self.bom_id.id]])
 			
			i=0;
			for line in bom_line_id:
				updated_qty = 0;
				if pro_qty[i]:
					updated_qty = pro_qty[i]
				res = {
						'p_r_p_qty':line.p_r_p_qty-updated_qty
					}
				i=i+1
				line.write(res)
			self.state = "draft"
	
	@api.multi
	def action_line_generate(self):
		if self.bom_id:
			res = []
			obj_purchase_line = self.env['purchase.requisition.line']
			bom_line_id = self.env['bom.consumption.line'].search(['|',['mc_yarn_id','=',self.bom_id.id],['mc_acc_id','=',self.bom_id.id]])
			
			if bom_line_id:
				for line in bom_line_id:
					res = {
							'requisition_id':self.id,
							'product_id':line.product_id.id,
							'product_qty':line.quantity-line.p_r_p_qty,
							'product_uom_id':line.uom_id.id,
							'schedule_date':self.schedule_date,
							'bom_line_id':line.id
						}
					obj_purchase_line.create(res)
				self.bom_flag = False
				self.bom_flag1 = True
				
	


class InheritedPurchaseRequisitionLine(models.Model):
	_inherit = 'purchase.requisition.line'

	bom_line_id = fields.Many2one('bom.consumption.line', string="BOM Line")
	
	@api.onchange('requisition_id')
	def onchange_requisition_id(self):
		res = {}
		if self.requisition_id.bom_id.id!=False:
			obj_bom_line = self.env['bom.consumption.line']
			bom_line = obj_bom_line.search(['|',['mc_yarn_id','=',self.requisition_id.bom_id.id],['mc_acc_id','=',self.requisition_id.bom_id.id]])
			product=[]
			for b_line in bom_line:
				product.append(b_line.product_id.id)
			res['domain'] = {'product_id': [('id', 'in', product)]}
		else:
			res['domain'] = {'product_id': False}
		return res

class InheritedBomConsumptionLine(models.Model):
	_inherit = 'bom.consumption.line'

	p_r_p_qty = fields.Float(string="Purchase Req. Quantity", digits=(10, 2))
	
					