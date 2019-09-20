from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError


class StockTransferSummaryWizard(models.TransientModel):
    _name = 'stock.transfer.summary.wizard'

    date_from = fields.Date("Date From", required=True)
    date_to = fields.Date("Date To", required=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Unit Name', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)
    category_id = fields.Many2one('product.category', string='Category', required=False)

    @api.constrains('date_from', 'date_to')
    def _check_date_validation(self):
        if self.date_from > self.date_to:
            raise ValidationError(_("From date must be less then To date."))

    @api.multi
    def report_print(self):
        location = self.env['stock.location'].search(
            [('operating_unit_id', '=', self.operating_unit_id.id), ('name', '=', 'Stock')])

        if not location:
            raise UserError(_("There are no stock location for this unit. "
                          "\nPlease create stock location for this unit."))

        data = {}
        data['date_from'] = self.date_from
        data['date_to'] = self.date_to
        data['operating_unit_id'] = self.operating_unit_id.id
        data['operating_unit_name'] = self.operating_unit_id.name
        data['location_id'] = location.id
        data['category_id'] = self.category_id.id

        return self.env['report'].get_action(self, 'stock_transfer_report.sts_report_temp', data=data)
