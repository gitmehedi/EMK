from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class MultiVariantInventoryReportWizard(models.TransientModel):
    _name = 'multi.variant.inventory.report.wizard'
    _description = 'Multi Variant Inventory Report'

    date_from = fields.Date("Date From", required=True)
    date_to = fields.Date("Date To", required=True)

    @api.constrains('date_from', 'date_to')
    def _check_date_range(self):
        if self.date_from > self.date_to:
            raise ValidationError(_("From date must be less then To date."))

    product_categ_id = fields.Many2one('product.category', string='Category', required=True)

    product_tmpl_id = fields.Many2one('product.template', string='Product', required=True)

    product_ids = fields.Many2many('product.product', string='Product')

    def _get_operating_unit(self):
        domain = [("id", "in", self.env.user.operating_unit_ids.ids)]
        return domain

    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', required=True,
                                        domain=_get_operating_unit
                                        )

    @api.multi
    def export_excel(self):
        return self.env['report'].get_action(self,
                                             report_name='goods_movement_ledger_reports.multi_variant_inventory_report_xlsx')
