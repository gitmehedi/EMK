from odoo import api, fields, models


class CnfQuotationWizard(models.TransientModel):
    _name = 'cnf.quotation.wizard'


    @api.multi
    def save_cnf_quotation(self):

        form_id = self.env.context.get('active_id')
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.search([('id', '=', form_id)])
        shipment_obj.write({'state': 'cnf_quotation'})
        return {'type': 'ir.actions.act_window_close'}










