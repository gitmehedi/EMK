from odoo import fields, models, api


class InheritedAccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    def _get_default_lc_pad_account_id(self):
        return self.env.user.company_id.lc_pad_account

    lc_pad_account = fields.Many2one('account.account', 'LC Goods In Transit Account',
                                     default=lambda self: self._get_default_lc_pad_account_id())

    @api.multi
    def set_lc_pad_account_id(self):
        if self.lc_pad_account and self.lc_pad_account != self.company_id.lc_pad_account:
            self.company_id.write({'lc_pad_account': self.lc_pad_account.id})
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'lc_pad_account', self.lc_pad_account.id)

    def _get_default_foreign_ap_account(self):
        return self.env.user.company_id.foreign_ap_account

    foreign_ap_account = fields.Many2one('account.account', 'Foreign AP Clearing Account',
                                         default=lambda self: self._get_default_foreign_ap_account())

    @api.multi
    def set_foreign_ap_account(self):
        if self.foreign_ap_account and self.foreign_ap_account != self.company_id.foreign_ap_account:
            self.company_id.write({'foreign_ap_account': self.foreign_ap_account.id})
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'foreign_ap_account', self.foreign_ap_account.id)


class ResCompany(models.Model):
    _inherit = "res.company"

    lc_pad_account = fields.Many2one('account.account', string='LC PAD Account')
    foreign_ap_account = fields.Many2one('account.account', string='Export Clearing Account')
