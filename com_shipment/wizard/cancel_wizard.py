from odoo import api, fields, models


class CancelWizard(models.TransientModel):
    _name = 'cancel.wizard'

    comments = fields.Text('Comments', required=True, help="Would you like to leave a message?")

    @api.multi
    def save_done(self):

        form_id = self.env.context.get('active_id')
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.search([('id', '=', form_id)])
        shipment_obj.write(
            {'comment': self.comments, 'state': 'cancel'})
        return {'type': 'ir.actions.act_window_close'}

