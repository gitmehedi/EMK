from odoo import api, fields, models


class BuyerBankExportWizard(models.TransientModel):
    _name = 'to.buyer.bank.export.foreign.wizard'

    to_buyer_bank_date = fields.Date('Buyer Bank Receive', required=True)

    @api.multi
    def save_action(self):

        form_id = self.env.context.get('active_id')
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.search([('id', '=', form_id)])
        if shipment_obj:
            shipment_obj.write({'to_buyer_bank_date': self.to_buyer_bank_date,
                                'state': 'to_buyer_bank'})
            return {'type': 'ir.actions.act_window_close'}






