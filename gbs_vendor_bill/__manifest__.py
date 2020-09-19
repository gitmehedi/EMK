# -*- coding: utf-8 -*-
{
    'name': 'GBS Vendor Bill (Samuda)',
    'description': """ Extended module to manage Vendor Bill.""",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '10.0.0.1',
    'category': 'Accounting',
    'depends': [
        'account_invoice_merge_attachment',
        'account_operating_unit',
        'base_suspend_security',
        'purchase',
    ],
    'data': [
        'views/account_config.xml',
        'views/invoice_merge_view.xml',
        'views/account_invoice_view.xml',
    ],
    'installable': True,
    'application': False,
}