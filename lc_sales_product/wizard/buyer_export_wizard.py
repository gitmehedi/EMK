from odoo import api, fields, models


class BuyerExportWizard(models.TransientModel):
    _name = 'to.buyer.export.wizard'

    to_buyer_date = fields.Date('Dispatch to Party', required=True)

    @api.multi
    def save_action(self):

        form_id = self.env.context.get('active_id')
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.search([('id', '=', form_id)])
        if shipment_obj:
            shipment_obj.write({'to_buyer_date': self.to_buyer_date,
                                'state': 'to_buyer'})
            return {'type': 'ir.actions.act_window_close'}






