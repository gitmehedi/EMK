from odoo import api, fields, models


class CnfQuotationWizard(models.TransientModel):
    _name = 'cnf.clear.wizard'

    arrival_date = fields.Date('Arrival Date', required=True)

    @api.multi
    def save_cnf_clear(self):

        form_id = self.env.context.get('active_id')
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.search([('id', '=', form_id)])
        shipment_obj.write({'arrival_date': self.arrival_date, 'state': 'cnf_clear'})
        return {'type': 'ir.actions.act_window_close'}










