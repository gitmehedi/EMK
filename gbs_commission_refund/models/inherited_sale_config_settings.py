from odoo import api, fields, models


class SaleConfigSettings(models.TransientModel):
    _inherit = "sale.config.settings"

    def _get_default_commission_start_date(self):
        return self.env['ir.values'].sudo().get_default('sale.config.settings', 'commission_start_date')

    commission_start_date = fields.Date(string="Commission and Refund Start On")

    @api.multi
    def set_commission_start_date(self):
        return self.env['ir.values'].sudo().set_default(
            'sale.config.settings',
            'commission_start_date',
            self.commission_start_date
        )
