from odoo import api, fields, models
from odoo.exceptions import Warning
import re

class InheritedAccountAccount(models.Model):
    _inherit = "account.account"

    @api.constrains('code')
    def _check_code_number(self):

        if self.code and not self.code.isdecimal():
            raise Warning('Code must be a Number')
