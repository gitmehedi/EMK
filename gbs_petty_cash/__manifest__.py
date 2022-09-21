# -*- coding: utf-8 -*-
{
    'name': "GBS Petty Cash",

    'summary': """""",

    'description': """
    """,

    'author': "Shoaib Ahmed",

    'category': 'Accounting',
    'version': '10.0.1',

    'depends': ['account', 'account_operating_unit', 'gbs_samuda_account_access'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'report/petty_cash_report_xlsx_view.xml',
        'views/inherited_account_journal_view.xml',
        'views/inherited_account_bank_statement_view.xml',
        'views/petty_cash_dashboard.xml',
        'views/inherited_account_bank_statement_view.xml',
        'views/account_bank_statement_popup.xml',
        'views/inherited_account_move_line.xml'
    ],
}
