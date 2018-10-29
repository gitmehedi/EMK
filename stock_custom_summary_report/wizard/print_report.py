from odoo import api, fields, models , _
from odoo.exceptions import ValidationError,UserError


class StockInventoryWizard(models.TransientModel):
    _name = 'stock.inventory.wizard'

    date_from = fields.Date("Date From", required=True)
    date_to = fields.Date("Date To", required=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Unit Name', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)
    category_id = fields.Many2one('product.category', string='Category', required=False)
    product_id = fields.Many2one('product.product', string='Product')
    report_type_ids = fields.Many2many('report.type.selection', string="Report Type")

    @api.constrains('date_from', 'date_to')
    def _check_date_validation(self):
        if self.date_from > self.date_to:
            raise ValidationError(_("From date must be less then To date."))

    @api.multi
    def report_print(self):
        location = self.env['stock.location'].search([('operating_unit_id', '=', self.operating_unit_id.id),('name', '=', 'Stock')])

        if not location:
            raise UserError(_("There are no stock location for this unit. "
                          "\nPlease create stock location for this unit."))

        report_type = [val.code for val in self.env['report.type.selection'].search([])]
        selected_type = [val.code for val in self.report_type_ids]

        data = {}
        data['date_from'] = self.date_from
        data['date_to'] = self.date_to
        data['location_id'] = location.id
        data['operating_unit_id'] = self.operating_unit_id.id
        data['operating_unit_name'] = self.operating_unit_id.name
        data['category_id'] = self.category_id.id
        data['product_id'] = self.product_id.id
        data['report_type'] = selected_type if len(selected_type) > 0 else report_type

        return self.env['report'].get_action(self, 'stock_custom_summary_report.stock_report_template',
                                             data=data)
