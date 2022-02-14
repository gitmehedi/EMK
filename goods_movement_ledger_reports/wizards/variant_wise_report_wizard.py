from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class VariantWiseReportWizard(models.TransientModel):
    _name = 'variant.wise.report.wizard'
    _description = 'Variant Wise Report'

    date_from = fields.Date("Date From", required=True)
    date_to = fields.Date("Date To", required=True)

    @api.constrains('date_from', 'date_to')
    def _check_date_range(self):
        if self.date_from > self.date_to:
            raise ValidationError(_("From date must be less then To date."))

    @api.multi
    def _get_products(self):
        if self.env.user.has_group('mrp.group_mrp_user'):
            if self.env.user.has_group('mrp_gbs_access.group_mrp_adviser'):
                domain = [("id", "in", self.env['product.product'].sudo().search([('manufacture_ok', '=', True)]).ids)]
                return domain
            else:
                # if mrp manager he will view only allowed products, mrp advisor will view all products
                domain = [("id", "in", self.env.user.product_ids.ids)]
                return domain
        elif self.env.user.has_group('mrp_gbs_access.group_mrp_adviser'):
            domain = [("id", "in", self.env['product.product'].sudo().search([('manufacture_ok', '=', True)]).ids)]
            return domain
        else:
            raise UserError(_('Manufacturing group not set to the user!'))

    # product_ids = fields.Many2many('product.product', 'product_product_rel', string='Products', required=True,
    #                                domain=_get_products)

    product_id = fields.Many2one('product.product', string='Product', required=True, domain=_get_products)

    def _get_operating_unit(self):
        domain = [("id", "in", self.env.user.operating_unit_ids.ids)]
        return domain

    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', required=True,
                                        domain=_get_operating_unit
                                        )

    @api.multi
    def export_excel(self):
        return self.env['report'].get_action(self,
                                             report_name='goods_movement_ledger_reports.variant_wise_report_xlsx')
