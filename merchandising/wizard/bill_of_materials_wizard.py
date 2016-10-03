from openerp import api, exceptions, fields, models
from openerp.addons.helper import validator

class BillOfMaterialsWizard(models.TransientModel):
    _name = "bill.materials.wizard"
    
    export_po_id = fields.Many2one('buyer.work.order', string="Export PO",
                                             domain=[('state', '=', 'confirm')])
      
    # create a function that will save the info from your wizard into your model (active_id is the id of the record you called the wizard from, so you will save the info entered in wizard is that record)
    @api.multi
    def generate_bill_materials(self):
        mc_ins = self.env['material.consumption']
        bwo_ins = self.env['buyer.work.order']
        
        bwo_data = bwo_ins.search([('id', '=', self.export_po_id.id)])[0]
        mc_data = bwo_ins.search([('name','=',bwo_data.name)])
        
        
#         validator.debug(vals)
#         validator.debug(context)
        
#         active_id = context.get('active_id', False)
#         data = self.browse(self._context.get('active_ids'))
#         validator.debug(self._context.get('active_ids'))
#         validator.debug(data)
#         validator.debug(bwo_data.name)
#         for idsdafasd in bwo_data:
#             validator.debug(idsdafasd.name)
        
#         slip_ids = []
#         if context is None:
#             context = {}
#         
#         run_data = {}
#         mc = mc_pool.browse(cr, uid, data.material_consumption_id.id, context)
#         
#         for line in mc.yarn_ids:
#             vals = {
#                 'mc_yarn_id': mc_id,
#                 'quantity': line.quantity,
#                 'wastage': line.wastage,
#                 'product_id': line.product_id.id,
#                 'uom_id': line.uom_id.id,
#                 'preffered_supplier_id': line.preffered_supplier_id.id,
#                 'buyer_mentioned_supplier_id': line.buyer_mentioned_supplier_id.id,
#                 'status': line.status,
#             }
#             mcd_pool.create(cr, uid, vals, context=context)
#             
#         for line in mc.acc_ids:
#             vals = {
#                 'mc_acc_id': mc_id,
#                 'quantity': line.quantity,
#                 'wastage': line.wastage,
#                 'product_id': line.product_id.id,
#                 'uom_id': line.uom_id.id,
#                 'preffered_supplier_id': line.preffered_supplier_id.id,
#                 'buyer_mentioned_supplier_id': line.buyer_mentioned_supplier_id.id,
#                 'status': line.status,
#             }
#             mcd_pool.create(cr, uid, vals, context=context)
            
        return {'type': 'ir.actions.act_window_close'}
