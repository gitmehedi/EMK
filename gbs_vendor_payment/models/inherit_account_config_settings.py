from odoo import fields, models, api

class ResCompany(models.Model):
    _inherit = "res.company"

    post_difference_account = fields.Many2one('account.account', string='LC PAD Account')

class InheritedAccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    def _get_default_post_difference_account_id(self):
        if self.env.user.company_id.post_difference_account:
            return self.env.user.company_id.post_difference_account
        else:
            return False

    post_difference_account = fields.Many2one('account.account', 'Post Difference Account',
                                              default=lambda self: self._get_default_post_difference_account_id())

    @api.multi
    def set_post_difference_account_id(self):
        if self.post_difference_account and self.post_difference_account != self.company_id.post_difference_account:
            self.company_id.write({'post_difference_account': self.post_difference_account.id})
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'post_difference_account', self.post_difference_account.id)



