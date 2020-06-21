from odoo import fields, models


class InheritedProductProduct(models.Model):
    _inherit = 'product.product'

    is_provisional_expense = fields.Boolean('Provisional Expense', default=False)