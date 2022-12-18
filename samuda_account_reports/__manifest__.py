{
    'name': 'Samuda Account Reports',
    'version': '10.0.0.1',
    'author': 'Genweb2',
    'website': 'www.genweb2.com',
    'category': 'Accounting',
    'depends': [
        'account_reports',
        'analytic',
        'report_xlsx',
        'report',
        'gbs_account'
    ],
    'summary': "This module generate custom account reports",
    'description': """Different type of account reports""",
    'data': [
        'reports/profit_loss_with_realization_xlsx_view.xml',
        'reports/account_general_ledger_xlsx_view.xml',
        'reports/analytic_account_xlsx_view.xml',
        'reports/cost_sheet_xlsx_view.xml',
        'reports/account_general_ledger_details_xlsx_view.xml',
        'wizard/profit_loss_with_realization_view.xml',
        'wizard/account_general_ledger_wizard_view.xml',
        'wizard/analytic_account_wizard_view.xml',
        'wizard/cost_sheet_wizard_view.xml',
        'wizard/account_general_ledger_details_wizard_view.xml'
    ],
    'installable': True,
    'application': False,
}
