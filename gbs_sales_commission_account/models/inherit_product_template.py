from odoo import fields, models


class InheritProductTemplate(models.Model):
    _inherit='product.template'

    commission_expense = fields.Many2one('account.account', string='Commission Expense')



class InheritResCompany(models.Model):
    _inherit='res.company'

    commission_journal = fields.Many2one('account.journal', string='Commission Journal')

