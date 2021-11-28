from odoo import fields, models, api


class InheritedOperatingUnit(models.Model):
    _inherit = 'operating.unit'

    payable_account = fields.Many2one('account.account', string='Payable GL')
    tds_payable_account = fields.Many2one('account.account', string='TDS Payable GL')
    telephone_bill_account = fields.Many2one('account.account', string='Telephone Bill GL')
    employee_pf_contribution_account = fields.Many2one('account.account', string='Employee PF Contribution GL')
    company_pf_contribution_account = fields.Many2one('account.account', string='Company PF Contribution GL')

    default_debit_account = fields.Many2one('account.account', string='Default Salary Debit GL')
    default_festival_debit_account = fields.Many2one('account.account', string='Default Festival Debit GL')
    debit_account_ids = fields.One2many('department.account.map', 'operating_unit_id',
                                        string="""Salary Debit GL's""")
    festival_debit_account_ids = fields.One2many('department.account.map', 'festival_operating_unit_id',
                                              string="""Bonus Debit GL's""")

