from odoo import api, exceptions, fields, models


class PurchaseReportWizard(models.TransientModel):
    _name = 'purchase.report.wizard'

    date_from = fields.Date("Date from",required=True)
    date_to = fields.Date("Date to",required=True)
    partner_id = fields.Many2one('res.partner', string='Supplier')
    operating_unit_id = fields.Many2one('operating.unit', string='Unit Name', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)

    @api.multi
    def report_print(self):
        location = self.env['stock.location'].search(
            [('operating_unit_id', '=', self.operating_unit_id.id), ('name', '=', 'Stock')])

        data = {}
        data['date_from'] = self.date_from
        data['date_to'] = self.date_to
        data['partner_id'] = self.partner_id.id
        data['location_id'] = location.id
        data['operating_unit_id'] = self.operating_unit_id.id
        data['operating_unit_name'] = self.operating_unit_id.name

        return self.env['report'].get_action(self, 'stock_purchase_custom_report.purchase_report_template',
                                             data=data)