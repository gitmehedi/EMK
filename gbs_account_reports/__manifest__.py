# -*- coding: utf-8 -*-
{
    'name': 'GBS Accounting Reports',
    'summary': 'Add operating unit features on accounting reports',
    'description': """
Accounting Reports
====================
    """,
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '10.0.0.1',
    'category': 'Accounting',
    'depends': ['account_reports'],
    'data': [
        'data/lib_data.xml',
    ],
    'qweb': [
            'static/src/xml/gbs_account_report_backend.xml',
        ],
    'installable': True,
    'application': False,
}