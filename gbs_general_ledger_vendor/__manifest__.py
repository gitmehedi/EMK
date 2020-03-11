# -*- coding: utf-8 -*-

{
    'name': 'Vendor General Ledger Reports',
    'version': '10.0.0.1',
    'category': 'Reporting',
    'summary': 'Vendor General Ledger Reports in Excel and Pdf format.',
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'depends': [
        'account',
        'report_xlsx',
        'report',
    ],
    'data': [
        'report/vendor_general_ledger_xlsx_view.xml',
        'wizard/vendor_general_ledger_wizard_view.xml',
    ],
    'installable': True,
    'application': False,
}