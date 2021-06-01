from odoo import api, fields, models, _


class DeliveryReportWizard(models.TransientModel):
    _name = 'delivery.report.wizard'

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', domain="([('customer','=','True')])")
    product_tmpl_id = fields.Many2one('product.template', string='Product', domain="([('sale_ok','=','True')])")
    product_id = fields.Many2one('product.product', string='Product Variant', domain="([('sale_ok','=','True')])")
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', required=True,
                                        domain=lambda self: [("id", "in", self.env.user.operating_unit_ids.ids)])

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        if self.product_tmpl_id:
            return {'domain': {'product_id': [('product_tmpl_id', '=', self.product_tmpl_id.id)]}}
        else:
            return {'domain': {'product_id': [('sale_ok', '=', 'True')]}}

    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        return self.env['report'].get_action(self, report_name='delivery_reports.delivery_report_xlsx')
