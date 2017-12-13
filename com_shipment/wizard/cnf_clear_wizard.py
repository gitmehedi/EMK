from odoo import api, fields, models


class CnfQuotationWizard(models.TransientModel):
    _name = 'cnf.clear.wizard'

    arrival_date = fields.Date('Arrival Date', required=True)
    transport_by = fields.Char('Transport By', required=True)
    vehical_no = fields.Char('Vehical No', required=True)
    employee_ids = fields.Many2many('hr.employee', string='''Employee's''')
    notes = fields.Text('Notes')

    @api.multi
    def save_cnf_clear(self):

        form_id = self.env.context.get('active_id')
        shipment_pool = self.env['purchase.shipment']
        shipment_obj = shipment_pool.search([('id', '=', form_id)])
        if shipment_obj:
            shipment_obj.write({'arrival_date': self.arrival_date,
                                'transport_by': self.transport_by,
                                'vehical_no': self.vehical_no,
                                'state': 'cnf_clear'})
            return {'type': 'ir.actions.act_window_close'}






