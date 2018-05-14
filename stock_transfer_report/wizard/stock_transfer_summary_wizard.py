from odoo import api, fields, models


class StockTransferSummaryWizard(models.TransientModel):
    _name = 'stock.transfer.summary.wizard'

    date_from = fields.Date("Date from", required=True)
    date_to = fields.Date("Date to", required=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Unit Name', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)

    @api.multi
    def report_print(self):
        location = self.env['stock.location'].search(
            [('operating_unit_id', '=', self.operating_unit_id.id), ('name', '=', 'Stock')])

        address = []
        if self.operating_unit_id.partner_id.street:
            address.append(self.operating_unit_id.partner_id.street)

        if self.operating_unit_id.partner_id.street2:
            address.append(self.operating_unit_id.partner_id.street2)

        if self.operating_unit_id.partner_id.zip_id:
            address.append(self.operating_unit_id.partner_id.zip_id.name)

        if self.operating_unit_id.partner_id.city:
            address.append(self.operating_unit_id.partner_id.city)

        if self.operating_unit_id.partner_id.state_id:
            address.append(self.operating_unit_id.partner_id.state_id.name)

        if self.operating_unit_id.partner_id.country_id:
            address.append(self.operating_unit_id.partner_id.country_id.name)

        str_address = ', '.join(address)


        data = {}
        data['date_from'] = self.date_from
        data['date_to'] = self.date_to
        data['operating_unit_id'] = self.operating_unit_id.id
        data['operating_unit_name'] = self.operating_unit_id.name
        data['location_id'] = location.id
        data['str_address'] = str_address

        return self.env['report'].get_action(self, 'stock_transfer_report.sts_report_temp', data=data)
