from odoo import api, fields, models


class DocReceiveWizard(models.TransientModel):
    _name = 'doc.receive.wizard'

    bill_of_lading_number = fields.Char(string='BoL Number', required=True, help="Bill Of Lading Number")
    shipment_date = fields.Date('Ship on Board', required=True)

    # Packing List
    gross_weight = fields.Float('Gross Weight', required=True)
    net_weight = fields.Float('Net Weight', required=True)

    @api.multi
    def save_doc_receive(self):

        form_id = self.env.context.get('active_id')
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.search([('id', '=', form_id)])
        shipment_obj.write({'bill_of_lading_number': self.bill_of_lading_number,
                            'shipment_date': self.shipment_date,
                            'gross_weight': self.gross_weight,
                            'net_weight': self.net_weight,
                            'state': 'receive_doc'})
        return {'type': 'ir.actions.act_window_close'}










