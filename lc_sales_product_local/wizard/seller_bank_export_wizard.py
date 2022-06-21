from odoo import api, fields, models


class SellerBankExportWizard(models.TransientModel):
    _name = 'to.seller.bank.export.wizard'

    to_seller_bank_date = fields.Date('Saller Bank Receive', required=True)

    @api.multi
    def save_action(self):

        form_id = self.env.context.get('active_id')
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.search([('id', '=', form_id)])
        if shipment_obj:
            shipment_obj.write({'to_seller_bank_date': self.to_seller_bank_date,
                                'state': 'to_seller_bank'})
            return {'type': 'ir.actions.act_window_close'}






