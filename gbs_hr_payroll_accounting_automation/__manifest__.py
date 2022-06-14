{
    'name': 'GBS HR Payroll Accounting Automation',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',

    'category': 'Payroll',
    'version': '10.0.1.0.0',
    'depends': ['base', 'hr_payroll', 'account', 'gbs_operating_unit', 'gbs_employee_cost_center_link', 'hr_payroll_ot'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/account_journal_data.xml',
        'data/sequence.xml',
        'views/operating_units_new_views.xml',
        'views/inherit_hr_payslip_run_view.xml',
        'views/create_provision_views.xml',
        'wizard/confirmation_wizard.xml',
        'wizard/success_wizard.xml',
    ],

}
