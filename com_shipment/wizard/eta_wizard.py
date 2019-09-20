from odoo import api, fields, models


class ETAWizard(models.TransientModel):
    _name = 'eta.wizard'

    eta_date = fields.Date('ETA Date', required=True, help="Estimated Time of Arrival")

    @api.multi
    def save_eta(self):

        form_id = self.env.context.get('active_id')
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.search([('id', '=', form_id)])
        shipment_obj.write({'eta_date': self.eta_date, 'state': 'eta'})
        return {'type': 'ir.actions.act_window_close'}










