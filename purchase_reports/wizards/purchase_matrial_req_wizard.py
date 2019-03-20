from odoo import models, fields, api

class PurchaseMaterialWizard(models.TransientModel):
    _name = "purchase.material.requisition.wizard"

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit',required=True)
    dept_location_id = fields.Many2one('stock.location', string='Department', required=True,
                                       domain="[('operating_unit_id','=',operating_unit_id),('usage','=','departmental')]")
    date_from = fields.Date("Date From", required=True)
    date_to = fields.Date("Date To", required=True)

    @api.multi
    def process_print(self):
        data = {}
        data['report_type'] = self.env.context.get('type')
        data['operating_unit_id'] = self.operating_unit_id.name
        data['dept_location_id'] = self.dept_location_id.name
        data['date_from'] = self.date_from
        data['date_to'] = self.date_to

        return self.env['report'].get_action(self, 'purchase_reports.report_purchase_material_requisition', data=data)
