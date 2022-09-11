from odoo import models,fields,api,_

class ProductTemplate(models.Model):
    _inherit = "product.template"


    property_account_income_id = fields.Many2one('account.account', )
    property_account_expense_id = fields.Many2one('account.account',)
