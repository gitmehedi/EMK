from odoo import api, fields, models
from odoo.exceptions import Warning


class InheritedAccountAccount(models.Model):
    _inherit = "account.account"

    @api.constrains('code')
    def _add_code_suffix(self):
        if self.code and self.code.isalnum():
            raise Warning('Code must be a Number')








