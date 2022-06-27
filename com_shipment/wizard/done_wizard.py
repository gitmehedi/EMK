from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning

class DoneWizard(models.TransientModel):
    _name = 'done.wizard'

    comments = fields.Text('Comments', required=True, help="Would you like to leave a message?")
    shipment_done_date = fields.Date(string='Shipment Done Date')
    ait_amount = fields.Float(string='AIT Amount')
    payment_rec_date = fields.Date(string='Payment Rec. Date')
    payment_rec_amount = fields.Float(string='Payment Rec. Amount', default=lambda self: self._get_default_shipment_invoice_values())
    payment_charge = fields.Float(string='Payment Charge')
    discrepancy_amount = fields.Float(string='Discrepancy Amount')
    region_type = fields.Selection([('local', "Local"),('foreign', "Foreign")], readonly=True,)

    @api.multi
    def save_done(self):
        if self.ait_amount < 0:
            raise UserError("AIT amount is wrong")
        if self.payment_rec_amount < 0:
            raise UserError("Payment receive amount is wrong")
        if self.payment_charge < 0:
            raise UserError("Payment Charge is wrong")
        if self.discrepancy_amount < 0:
            raise UserError("Discrepancy amount is wrong")

        form_id = self.env.context.get('active_id')
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.search([('id', '=', form_id)])
        shipment_obj.write(
            {
                'comment': self.comments,
                'shipment_done_date': self.shipment_done_date,
                'ait_amount': self.ait_amount,
                'payment_rec_date': self.payment_rec_date,
                'payment_rec_amount': self.payment_rec_amount - (self.ait_amount + self.payment_charge + self.discrepancy_amount),
                'payment_charge': self.payment_charge,
                'discrepancy_amount': self.discrepancy_amount,
                'state': 'done'
            })
        return {'type': 'ir.actions.act_window_close'}

    def _get_default_shipment_invoice_values(self):
        shipment_id = self.env.context.get('active_id')
        shipment = self.env['purchase.shipment'].search([('id', '=', shipment_id)])
        invoice_value = 0
        if shipment:
            invoice_value = shipment.invoice_value
        return invoice_value

    @api.onchange('ait_amount', 'payment_charge', 'discrepancy_amount')
    def _calculate_payment_rec_amount(self):
        shipment_id = self.env.context.get('active_id')
        shipment = self.env['purchase.shipment'].search([('id', '=', shipment_id)])
        invoice_value = 0
        if shipment:
            invoice_value = shipment.invoice_value
        self.payment_rec_amount = invoice_value - (self.ait_amount + self.payment_charge + self.discrepancy_amount)
        