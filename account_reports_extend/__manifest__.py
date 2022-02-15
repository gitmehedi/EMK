# -*- coding: utf-8 -*-
{
    'name': 'Accounting Reports Extend',
    'summary': 'Overwrite section name.',
    'description': """
Accounting Reports
====================
    """,
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '10.0.0.1',
    'category': 'Accounting',
    'depends': ['base', 'account_reports', 'gbs_application_group'],
    'data': [
        'data/inherit_account_financial_report_data.xml',
        'views/account_financial_report_view.xml'
    ],
    'installable': True,
    'application': False,
}
