from odoo import api, fields, models, _

class ResCompany(models.Model):
    _inherit = "res.company"

    security_deposit_account_id = fields.Many2one('account.account', string='Security Deposit Account',
                                                  help="Account for Security Deposit")
    head_branch_id = fields.Many2one('operating.unit', string='Head Branch')


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    def _get_default_account_id(self):
        return self.env.user.company_id.security_deposit_account_id

    def _get_default_head_branch_id(self):
        return self.env.user.company_id.head_branch_id

    security_deposit_account_id = fields.Many2one('account.account',string='Security Deposit Account',required=True,
                                                  default=lambda self: self._get_default_account_id(),
                                                  help="Account for Security Deposit")
    head_branch_id = fields.Many2one('operating.unit', string='Head Branch',
                                     default=lambda self: self._get_default_head_branch_id())

    @api.multi
    def set_security_deposit_account_id(self):
        if self.security_deposit_account_id and \
                        self.security_deposit_account_id != self.company_id.security_deposit_account_id:
            self.company_id.write({'security_deposit_account_id': self.security_deposit_account_id.id})
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'security_deposit_account_id', self.security_deposit_account_id.id)

    @api.multi
    def set_head_branch_id(self):
        if self.head_branch_id and self.head_branch_id != self.company_id.head_branch_id:
            self.company_id.write({'head_branch_id': self.head_branch_id.id})
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'head_branch_id', self.head_branch_id.id)
