from odoo import api, fields, models


class CnfQuotationWizard(models.TransientModel):
    _name = 'gate.in.wizard'


    @api.multi
    def save_gate_in(self):

        form_id = self.env.context.get('active_id')
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.search([('id', '=', form_id)])
        shipment_obj.write({'state': 'gate_in'})
        return {'type': 'ir.actions.act_window_close'}










