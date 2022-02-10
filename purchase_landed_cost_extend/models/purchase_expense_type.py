from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PurchaseExpenseType(models.Model):
    _name = 'purchase.expense.type'
    _inherit = ['purchase.expense.type', 'mail.thread']

    name = fields.Char(track_visibility='onchange')
    default_expense = fields.Boolean(track_visibility='onchange')
    calculation_method = fields.Selection(track_visibility='onchange')
    default_amount = fields.Float(track_visibility='onchange')

    @api.constrains('name')
    def _check_name(self):
        # Check for Unique Name
        if self.name:
            purchase_expense_types = self.search([('name', '=ilike', self.name.strip())])
            if len(purchase_expense_types.ids) > 1:
                raise ValidationError(_('[Unique Error] Name must be unique!'))

    @api.constrains('calculation_method')
    def _check_calculation_method(self):
        if self.calculation_method:
            purchase_expense_types = self.search([('calculation_method', '=', self.calculation_method)])
            if len(purchase_expense_types.ids) > 1:
                raise ValidationError(_('[Unique Error] Calculation method must be unique!'))
