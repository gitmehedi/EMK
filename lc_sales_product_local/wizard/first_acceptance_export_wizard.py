from odoo import api, fields, models


class BuyerExportWizard(models.TransientModel):
    _name = 'to.first.acceptance.export.wizard'

    to_first_acceptance_date = fields.Date('1st Acceptance Date', required=True)

    @api.multi
    def save_action(self):

        form_id = self.env.context.get('active_id')
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.search([('id', '=', form_id)])
        if shipment_obj:
            shipment_obj.write({'to_first_acceptance_date': self.to_first_acceptance_date,
                                'state': 'to_first_acceptance'})
            return {'type': 'ir.actions.act_window_close'}
