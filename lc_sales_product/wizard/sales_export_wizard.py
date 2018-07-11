from odoo import api, fields, models


class SalesExportWizard(models.TransientModel):
    _name = 'to.sales.export.wizard'

    to_sales_date = fields.Date('Dispatch to Sales', required=True)

    @api.multi
    def save_action(self):

        form_id = self.env.context.get('active_id')
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.search([('id', '=', form_id)])
        if shipment_obj:
            shipment_obj.write({'to_sales_date': self.to_sales_date,
                                'state': 'to_sales'})
            return {'type': 'ir.actions.act_window_close'}






