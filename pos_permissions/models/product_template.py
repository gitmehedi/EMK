from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_expense_account(self):
        account =True
        pass

    property_account_expense_id = fields.Many2one('account.account', default=_get_expense_account)
