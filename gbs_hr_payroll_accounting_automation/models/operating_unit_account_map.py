from odoo import fields, models, api


class OperatingUnitAccountMap(models.Model):
    _name = 'operating.unit.account.map'
    _description = 'Description'

    operating_unit = fields.Many2one('operating.unit', string='Operating Unit')
    payable_account = fields.Many2one('account.account', string='Payable Account')
    tds_payable_account = fields.Many2one('account.account', string='TDS Payable Account')
    telephone_bill_account = fields.Many2one('account.account', string='Telephone Bill Account')
    employee_pf_contribution_account = fields.Many2one('account.account', string='Employee PF Contribution Account')
    company_pf_contribution_account = fields.Many2one('account.account', string='Company PF Contribution Account')

    default_debit_account = fields.Many2one('account.account', string='Default Debit Account')

    debit_account_ids = fields.One2many('department.account.map', 'operating_unit_id',
                                        string='Debit Accounts')
