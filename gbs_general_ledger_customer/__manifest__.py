# -*- coding: utf-8 -*-

{
    'name': 'Customer General Ledger Reports',
    'version': '10.0.0.1',
    'category': 'Reporting',
    'summary': 'Customer General Ledger Reports in Excel and Pdf format.',
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'depends': [
        'account',
        'report_xlsx',
        'report',
    ],
    'data': [
        'report/customer_general_ledger_xlsx_view.xml',
        'wizard/customer_general_ledger_wizard_view.xml',
    ],
    'installable': True,
    'application': False,
}
