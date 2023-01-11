from odoo import api, fields, models


class SaleConfigSettings(models.TransientModel):
    _inherit = "sale.config.settings"

    def _get_default_commission_refund_top_up_account(self):
        config_ap_id = self.env['ir.values'].sudo().get_default('sale.config.settings',
                                                                'commission_refund_top_up_account')
        return int(config_ap_id) if config_ap_id else False

    commission_refund_top_up_account = fields.Many2one(
        'account.account',
        'Commission/Refund Top Up Debit Account',
        default=lambda self: self._get_default_commission_refund_top_up_account()
    )

    @api.multi
    def set_default_commission_refund_top_up_account(self):
        return self.env['ir.values'].sudo().set_default(
            'sale.config.settings',
            'commission_refund_top_up_account',
            self.commission_refund_top_up_account.id if self.commission_refund_top_up_account else False
        )

    def _get_default_commission_slab_account_journal(self):
        config_ap_id = self.env['ir.values'].sudo().get_default('sale.config.settings',
                                                                'commission_slab_account_journal')
        return int(config_ap_id) if config_ap_id else False

    commission_slab_account_journal = fields.Many2one(
        'account.journal',
        'Commission/Refund Top Up Journal',
        default=lambda self: self._get_default_commission_slab_account_journal()
    )

    @api.multi
    def set_default_commission_slab_account_journal(self):
        return self.env['ir.values'].sudo().set_default(
            'sale.config.settings',
            'commission_slab_account_journal',
            self.commission_slab_account_journal.id if self.commission_slab_account_journal else False
        )



