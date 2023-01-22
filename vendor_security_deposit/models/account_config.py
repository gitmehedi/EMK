from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    security_deposit_account_id = fields.Many2one('account.account', string='Security Deposit Account',
                                                  help="Account for Security Deposit",
                                                  domain=[('reconcile', '=', True)])


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    def _get_default_account_id(self):
        return self.env.user.company_id.security_deposit_account_id

    security_deposit_account_id = fields.Many2one('account.account', string='Security Deposit Account', required=True,
                                                  default=lambda self: self._get_default_account_id(),
                                                  help="Account for Security Deposit",
                                                  domain=[('reconcile', '=', True)])

    @api.multi
    def set_security_deposit_account_id(self):
        if self.security_deposit_account_id and \
                        self.security_deposit_account_id != self.company_id.security_deposit_account_id:
            self.company_id.write({'security_deposit_account_id': self.security_deposit_account_id.id})
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'security_deposit_account_id', self.security_deposit_account_id.id)
