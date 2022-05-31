from odoo import api, fields, models


class BuyerExportWizard(models.TransientModel):
    _name = 'to.second.acceptance.export.wizard'

    to_second_acceptance_date = fields.Date('2nd Acceptance Date', required=True)

    @api.multi
    def save_action(self):

        form_id = self.env.context.get('active_id')
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.search([('id', '=', form_id)])
        if shipment_obj:
            shipment_obj.write({'to_second_acceptance_date': self.to_second_acceptance_date,
                                'state': 'to_second_acceptance'})
            return {'type': 'ir.actions.act_window_close'}
