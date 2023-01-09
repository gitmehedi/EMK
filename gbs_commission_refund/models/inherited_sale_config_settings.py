from odoo import api, fields, models


class SaleConfigSettings(models.TransientModel):
    _inherit = "sale.config.settings"

    def _get_default_commission_refund_default_ap_parent_id(self):
        config_ap_id = self.env['ir.values'].sudo().get_default('sale.config.settings', 'commission_refund_default_ap_parent_id')
        return int(config_ap_id) if config_ap_id else False

    commission_refund_default_ap_parent_id = fields.Many2one(
        'account.account',
        'Commission/Refund Default AP Parent',
        default=lambda self: self._get_default_commission_refund_default_ap_parent_id()
    )

    @api.multi
    def set_commission_refund_default_ap_parent_id(self):
        return self.env['ir.values'].sudo().set_default(
            'sale.config.settings',
            'commission_refund_default_ap_parent_id',
            self.commission_refund_default_ap_parent_id.id if self.commission_refund_default_ap_parent_id else False
        )
