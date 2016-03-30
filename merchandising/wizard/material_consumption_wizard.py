from openerp import api, exceptions, fields, models
from openerp.addons.helper import validator

class MaterialConsumptionWizard(models.TransientModel):
    _name = "material.consumption.wizard"
    
    material_consumption_id = fields.Many2one('material.consumption', string="Material Consumption",
                                             domain=[('template', '=', 'True')])
      
    # create a function that will save the info from your wizard into your model (active_id is the id of the record you called the wizard from, so you will save the info entered in wizard is that record)
    @api.multi
    def geneate_template(self, context=None):
        mc_pool = self.env['material.consumption']
        mcd_pool = self.env['material.consumption.details']
        mc_id = context.get('active_id', False)
#         data = self.browse(self.material_consumption_id.ids)
        
        mc = mc_pool.browse(self.material_consumption_id.ids)
#         mcd_pool.yarn_ids.unlink()
#         mcd_pool.acc_ids.unlink()
        
        if mc.yarn_ids:
            for line in mc.yarn_ids:
                
                vals = {
                    'mc_yarn_id': mc_id,
                    'quantity': line.quantity,
                    'wastage': line.wastage,
                    'product_tmp_id': line.product_tmp_id.id,
                    'variant_ids': [(6, 0, line.variant_ids.ids)],
                    'uom_id': line.uom_id.id,
                    'preffered_supplier_id': line.preffered_supplier_id.id,
                    'buyer_mentioned_supplier_id': line.buyer_mentioned_supplier_id.id,
                    'status': line.status,
                }
#                 mcd_pool.variant_ids.create({'variant_id':1})
                line_id = mcd_pool.create(vals)
                
#                 line_id.variant_ids = (0, 0, line.variant_ids.ids)
#                 line_id.variant_ids = [(6, 0, res.get('invoice_line_tax_id'))]
#                 for v in line.variant_ids.ids:
#                     line_id.variant_ids.prod_attr_mat_cons_rel.create({'attr_id':v, 'mc_id':v})
                
                print line_id.variant_ids
        if mc.acc_ids:    
            for line in mc.acc_ids:
                vals = {
                    'mc_acc_id': mc_id,
                    'quantity': line.quantity,
                    'wastage': line.wastage,
                    'product_tmp_id': line.product_tmp_id.id,
                    'variant_ids': [(6, 0, line.variant_ids.ids)],
                    'uom_id': line.uom_id.id,
                    'preffered_supplier_id': line.preffered_supplier_id.id,
                    'buyer_mentioned_supplier_id': line.buyer_mentioned_supplier_id.id,
                    'status': line.status,
                }
                line_id = mcd_pool.create(vals)
            
        return {'type': 'ir.actions.act_window_close'}
