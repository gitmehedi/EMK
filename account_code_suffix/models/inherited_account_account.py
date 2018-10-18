from odoo import api, fields, models


class InheritedAccountAccount(models.Model):
    _inherit = "account.account"

    @api.constrains('code')
    def _add_code_suffix(self):
        if self.code:
            code_length_conf = self.env['account.code.length'].search([], limit=1)
            if len(self.code) < code_length_conf.account_code_length:
                self.code +='0'

