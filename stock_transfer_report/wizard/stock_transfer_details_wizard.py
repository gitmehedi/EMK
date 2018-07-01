from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockTransferDetailsWizard(models.TransientModel):
    _name = 'stock.transfer.details.wizard'

    date_from = fields.Date("Date From",required=True)
    date_to = fields.Date("Date To",required=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Unit Name', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)

    @api.constrains('date_from', 'date_to')
    def _check_date_validation(self):
        if self.date_from > self.date_to:
            raise ValidationError(_("From date must be less then To date."))

    @api.multi
    def report_print(self):
        location = self.env['stock.location'].search(
            [('operating_unit_id', '=', self.operating_unit_id.id), ('name', '=', 'Stock')])

        data = {}
        data['date_from'] = self.date_from
        data['date_to'] = self.date_to
        data['operating_unit_id'] = self.operating_unit_id.id
        data['operating_unit_name'] = self.operating_unit_id.name
        data['location_id'] = location.id

        return self.env['report'].get_action(self, 'stock_transfer_report.std_report_temp',data=data)