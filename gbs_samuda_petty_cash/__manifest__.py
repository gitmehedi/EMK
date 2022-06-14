{
    'name': 'Samuda Petty Cash',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Accounting',
    'version': '10.0.1.0.0',
    'depends': [
        'account', 'base', 'report_xlsx', 'report', 'gbs_application_group'
    ],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/account.xml',
        'views/inherited_acc_bank_statement_button_add_view.xml',
        'report/petty_cash_report_xlsx_view.xml'

    ],

    'summary': 'Petty Cash Implementation',
    'description':
        """Petty Cash Implementation""",
    'installable': True,
    'application': True,
}
