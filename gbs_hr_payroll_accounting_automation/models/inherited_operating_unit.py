from odoo import fields, models, api


class InheritedOperatingUnit(models.Model):
    _name = 'operating.unit'
    _inherit = ['operating.unit', 'mail.thread', 'ir.needaction_mixin']

    payable_account = fields.Many2one('account.account', track_visibility='onchange', string='Payable GL')
    tds_payable_account = fields.Many2one('account.account', track_visibility='onchange', string='TDS Payable GL')
    telephone_bill_account = fields.Many2one('account.account', track_visibility='onchange', string='Telephone Bill GL')
    employee_pf_contribution_account = fields.Many2one('account.account', track_visibility='onchange',
                                                       string='Employee PF Contribution GL')
    company_pf_contribution_account = fields.Many2one('account.account', track_visibility='onchange',
                                                      string='Company PF Contribution GL')

    default_debit_account = fields.Many2one('account.account', track_visibility='onchange',
                                            string='Default Salary Debit GL')
    default_festival_debit_account = fields.Many2one('account.account', track_visibility='onchange',
                                                     string='Default Festival Debit GL')
    debit_account_ids = fields.One2many('department.account.map', 'operating_unit_id',
                                        track_visibility='onchange', string="""Salary Debit GL's""")
    festival_debit_account_ids = fields.One2many('department.account.map', 'festival_operating_unit_id',
                                                 track_visibility='onchange', string="""Bonus Debit GL's""")

    payable_account_ot = fields.Many2one('account.account', track_visibility='onchange', string='OT Payable GL')

    default_debit_account_ot = fields.Many2one('account.account', track_visibility='onchange',
                                               string='OT Default Debit GL')
