from odoo import fields, models, api


class InheritedOperatingUnit(models.Model):
    _inherit = 'operating.unit'
    _description = 'Description'

    payable_account = fields.Many2one('account.account', string='Payable GL')
    tds_payable_account = fields.Many2one('account.account', string='TDS Payable GL')
    telephone_bill_account = fields.Many2one('account.account', string='Telephone Bill GL')
    employee_pf_contribution_account = fields.Many2one('account.account', string='Employee PF Contribution GL')
    company_pf_contribution_account = fields.Many2one('account.account', string='Company PF Contribution GL')

    default_debit_account = fields.Many2one('account.account', string='Default Debit GL')

    debit_account_ids = fields.One2many('department.account.map', 'operating_unit_id',
                                        string="""Debit GL's""")

