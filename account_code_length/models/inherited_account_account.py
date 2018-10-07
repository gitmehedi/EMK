from odoo import api, fields, models


class InheritedAccountAccount(models.Model):
    _inherit = "account.account"

    @api.constrains('code')
    def _check_code_length(self):
        code_str = self.code
        if code_str:
          code_str.upper()


