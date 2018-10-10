from odoo import api, fields, models


class InheritedAccountAccount(models.Model):
    _inherit = "account.account"

    @api.model
    def create(self, vals):
        vals['name'] = vals['name'].upper()
        return super(InheritedAccountAccount, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'name' in vals:
            vals['name'] = vals['name'].upper()
            return super(InheritedAccountAccount, self).write(vals)
