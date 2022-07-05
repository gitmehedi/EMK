from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

class InheritedAccountPayment(models.Model):
    _inherit = "account.payment"

    def _get_writeoff_account_id(self):
        post_difference_account = self.env['ir.values'].get_default('account.config.settings', 'post_difference_account')
        if not post_difference_account:
            raise UserError(
                _("Post Difference Account not set. Please contact your system administrator for "
                  "assistance."))

        return post_difference_account

    writeoff_account_id = fields.Many2one('account.account', string="Difference Account", default=_get_writeoff_account_id, domain=[('deprecated', '=', False)], copy=False)

