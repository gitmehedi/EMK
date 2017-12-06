from odoo import api, fields, models


class CnfQuotationWizard(models.TransientModel):
    _name = 'cnf.approve.quotation.wizard'


    @api.multi
    def save_cnf_approve_quotation(self):

        form_id = self.env.context.get('active_id')
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.search([('id', '=', form_id)])
        shipment_obj.write({'state': 'approve_cnf_quotation'})
        return {'type': 'ir.actions.act_window_close'}










