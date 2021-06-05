# -*- coding: utf-8 -*-

{
    'name': 'GBS Cheque Management',
    'version': '10.0.0.1',
    'category': 'Accounting',
    'summary': 'GBS Cheque Management',
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'depends': [
        'account',
        'report',
    ],
    'data': [
        # 'report/vendor_general_ledger_xlsx_view.xml',
        'wizard/cheque_print_wizard_view.xml',
    ],
    'installable': True,
    'application': False,
}