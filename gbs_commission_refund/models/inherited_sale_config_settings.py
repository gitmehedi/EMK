from odoo import api, fields, models


class SaleConfigSettings(models.TransientModel):
    _inherit = "sale.config.settings"

    def _get_default_commission_refund_default_ap_parent_id(self):
        config_ap_id = self.env['ir.values'].sudo().get_default('sale.config.settings', 'commission_refund_default_ap_parent_id')
        return int(config_ap_id) if config_ap_id else False

    commission_refund_default_ap_parent_id = fields.Many2one(
        'account.account',
        string='Commission/Refund Default AP Parent',
        default=lambda self: self._get_default_commission_refund_default_ap_parent_id(),
        domain="[('user_type_id.type', '=', 'view')]")


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

    @api.multi
    def set_commission_refund_default_ap_parent_id(self):
        return self.env['ir.values'].sudo().set_default(
            'sale.config.settings',
            'commission_refund_default_ap_parent_id',
            self.commission_refund_default_ap_parent_id.id if self.commission_refund_default_ap_parent_id else False
        )

    def _get_default_commission_journal_id(self):
        config_ap_id = self.env['ir.values'].sudo().get_default('sale.config.settings', 'commission_journal_id')
        return int(config_ap_id) if config_ap_id else False

    commission_journal_id = fields.Many2one(
        'account.journal',
        'Commission Journal',
        default=lambda self: self._get_default_commission_journal_id()
    )

    @api.multi
    def set_commission_journal_id(self):
        return self.env['ir.values'].sudo().set_default(
            'sale.config.settings',
            'commission_journal_id',
            self.commission_journal_id.id if self.commission_journal_id else False
        )

    def _get_default_refund_journal_id(self):
        config_ap_id = self.env['ir.values'].sudo().get_default('sale.config.settings', 'refund_journal_id')
        return int(config_ap_id) if config_ap_id else False

    refund_journal_id = fields.Many2one(
        'account.journal',
        'Refund Journal',
        default=lambda self: self._get_default_refund_journal_id()
    )

    @api.multi
    def set_refund_journal_id(self):
        return self.env['ir.values'].sudo().set_default(
            'sale.config.settings',
            'refund_journal_id',
            self.refund_journal_id.id if self.refund_journal_id else False
        )
