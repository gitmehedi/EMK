from odoo import api, fields, models
from odoo.exceptions import ValidationError


class InheritedAccountAccount(models.Model):
    _inherit = "account.account"

    @api.constrains('code')
    def _check_code_length(self):
        if self.code:
            code_length_conf = self.env['account.code.length'].search([], limit=1)
            if len(self.code) > code_length_conf.account_code_length:
                raise ValidationError(
                    'Code length can not be greater than %s characters' % (code_length_conf.account_code_length))
