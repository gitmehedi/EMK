from odoo import api, fields, models


class MaturityExportWizard(models.TransientModel):
    _name = 'to.maturity.export.wizard'

    to_maturity_date = fields.Date('Maturity Date', required=True)
    bill_id = fields.Char('Bill ID', required=True)

    @api.multi
    def save_action(self):

        form_id = self.env.context.get('active_id')
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.search([('id', '=', form_id)])
        if shipment_obj:
            shipment_obj.write({'to_maturity_date': self.to_maturity_date,
                                'bill_id': self.bill_id,
                                'state': 'to_maturity'})
            return {'type': 'ir.actions.act_window_close'}






