from openerp import api, exceptions, fields, models
from openerp.addons.helper import validator

class BillOfMaterialsWizard(models.TransientModel):
    _name = "bill.materials.wizard"
    
    export_po_id = fields.Many2one('sale.order', string="Export PO",
                                             domain=[('state', '=', 'confirm')])
      
    """ create a function that will save the info from your wizard into your model
    (active_id is the id of the record you called the wizard from,
    so you will save the info entered in wizard is that record) """

    @api.multi
    def generate_bill_materials(self):
        mc_ins = self.env['material.consumption']
        bwo_ins = self.env['sale.order']
        
        bwo_data = bwo_ins.search([('id', '=', self.export_po_id.id)])[0]
        mc_data = bwo_ins.search([('name','=',bwo_data.name)])
        
        return {'type': 'ir.actions.act_window_close'}
