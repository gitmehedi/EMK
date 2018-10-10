from odoo import api, fields, models
from odoo.exceptions import Warning


class InheritedAccountAccount(models.Model):
    _inherit = "account.account"


    @api.model
    def create(self, vals):
        vals['code'] = vals['code'].upper()
        return super(InheritedAccountAccount, self).create(vals)


    @api.multi
    def write(self, vals):

        if 'code' in vals:
            vals['code'] = vals['code'].upper()
            return super(InheritedAccountAccount, self).write(vals)