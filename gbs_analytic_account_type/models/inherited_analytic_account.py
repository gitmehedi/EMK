from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    type = fields.Selection([('cost', 'Cost Center'), ('profit', 'Profit Center'), ('revenue', 'Revenue Center'), ('investment', 'Investment Center')], string='Type')

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            aaa_objs = self.search([('name', '=', self.name), ('active', '=', True)])
            if len(aaa_objs.ids) > 1:
                raise ValidationError('The Analytic Account Name must be unique!')
