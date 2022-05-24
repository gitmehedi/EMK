from odoo import api, fields, models


class MaturityExportWizard(models.TransientModel):
    _name = 'to.maturity.export.wizard.foreign'

    to_maturity_date = fields.Date('Maturity Date', required=True)
    bill_id = fields.Char('Bill ID', required=True)
    bill_id = fields.Char('Bill ID', required=True)
    bl_date = fields.Date(string='BL Date', required=True)
    to_first_acceptance_date = fields.Date('1\'st Acceptance Date', track_visibility='onchange', required=True)

    @api.multi
    def save_action(self):

        form_id = self.env.context.get('active_id')
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.search([('id', '=', form_id)])
        if shipment_obj:
            shipment_obj.write({'to_maturity_date': self.to_maturity_date,
                                'bill_id': self.bill_id,
                                'bl_date': self.bl_date,
                                'to_first_acceptance_date': self.to_first_acceptance_date,
                                'state': 'to_maturity'})
            return {'type': 'ir.actions.act_window_close'}






