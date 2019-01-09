# -*- coding: utf-8 -*-
{
    'name': 'Account TDS',
    'description': """ Module is responsible for 'Tax Deducted at Source' Deduction""",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Account',
    'depends': [
        'date_range',
        'account'
    ],
    'data': [
        'views/account_tds_rule_view.xml',
        'views/inherit_date_range_view.xml',
    ],
    'installable': True,
    'application': True,
}
