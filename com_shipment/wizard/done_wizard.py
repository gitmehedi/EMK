from odoo import api, fields, models


class DoneWizard(models.TransientModel):
    _name = 'done.wizard'

    comments = fields.Text('Comments', required=True, help="Would you like to leave a message?")
    shipment_done_date = fields.Date(string='Shipment Done Date', required=False)
    ait_amount = fields.Float(string='Amount')
    payment_rec_date = fields.Date(string='Payment Rec. Date')
    payment_rec_amount = fields.Float(string='Payment Rec. Amount')
    payment_charge = fields.Float(string='Payment Charge')
    discrepancy_amount = fields.Float(string='Discrepancy Amount')
    discrepancy_details = fields.Char(string='Discrepancy Details')


    @api.multi
    def save_done(self):

        form_id = self.env.context.get('active_id')
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.search([('id', '=', form_id)])
        shipment_obj.write(
            {
                'comment': self.comments,
                'shipment_done_date': self.shipment_done_date,
                'ait_amount': self.ait_amount,
                'payment_rec_date': self.payment_rec_date,
                'payment_rec_amount': self.payment_rec_amount,
                'payment_charge': self.payment_charge,
                'discrepancy_amount': self.discrepancy_amount,
                'discrepancy_details': self.discrepancy_details,
                'state': 'done'
            })
        return {'type': 'ir.actions.act_window_close'}

