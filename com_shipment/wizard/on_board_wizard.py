from odoo import api, fields, models


class OnBoardWizard(models.TransientModel):
    _name = 'on.board.wizard'

    etd_date = fields.Date('ETD Date', required=True, help="Estimated Time of Departure")

    @api.multi
    def save_on_board(self):

        form_id = self.env.context.get('active_id')
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.search([('id', '=', form_id)])
        shipment_obj.write(
            {'etd_date': self.etd_date, 'state': 'on_board'})
        return {'type': 'ir.actions.act_window_close'}










