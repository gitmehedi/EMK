# -*- coding: utf-8 -*-
{
    'name': 'GBS Vendor Bill',
    'description': """ Extended module to manage Vendor Bill.""",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '10.0.0.1',
    'category': 'Accounting',
    'depends': [
        'account',
        'account_operating_unit',
        'sub_operating_unit',
    ],
    'data': [
        'views/account_invoice_view.xml',

    ],
    'installable': True,
    'application': True,
}
