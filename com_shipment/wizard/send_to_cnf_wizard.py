from odoo import api, fields, models


class SendCnfWizard(models.TransientModel):
    _name = 'send.to.cnf.wizard'

    cnf_received_date = fields.Date("Send To C&F", required=True)
    cnf_id = fields.Many2one('res.partner', "Supplier", required=True,
                             domain="[('is_cnf','=',True),('parent_id', '=', False)]")

    @api.multi
    def save_send_to_cnf(self):

        form_id = self.env.context.get('active_id')
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.search([('id', '=', form_id)])
        shipment_obj.write({'cnf_received_date': self.cnf_received_date, 'cnf_id': self.cnf_id.id,'state':'send_to_cnf'})
        return {'type': 'ir.actions.act_window_close'}

