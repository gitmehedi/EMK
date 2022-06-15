from odoo import api, fields, models


class BillIDExportWizard(models.TransientModel):
    _name = 'to.bill.id.export.wizard'

    bill_id = fields.Char('Bill ID', required=True)

    @api.multi
    def save_action(self):

        form_id = self.env.context.get('active_id')
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.search([('id', '=', form_id)])
        if shipment_obj:
            shipment_obj.write({'bill_id': self.bill_id,
                                'state': 'to_buyer_bank'})
            return {'type': 'ir.actions.act_window_close'}
