# -*- coding: utf-8 -*-

{
    'name': 'Account Reports',
    'version': '10.0.1.5.0',
    'category': 'Reporting',
    'summary': 'Account Reports',
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'depends': [
        'account',
        'report_xlsx',
        'report',
    ],
    'data': [
        'view/reports.xml',
        'wizard/trial_balance_wizard_view.xml',
    ],
    'installable': True,
    'application': False,
}
