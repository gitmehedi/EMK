from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class InheritAccountCostCenter(models.Model):
    _inherit = 'account.cost.center'

    @api.constrains('name')
    def constrains_name(self):
        # Check for Unique Name
        if self.name:
            acc_id = self.search([('name', '=ilike', self.name.strip())])
            if len(acc_id.ids) > 1:
                raise ValidationError(_('Name must be unique!'))

    @api.constrains('code')
    def constrains_code(self):
        # Check for Unique Name
        if self.code:
            acc_id = self.search([('code', '=ilike', self.code.strip())])
            if len(acc_id.ids) > 1:
                raise ValidationError(_('Code must be unique!'))
