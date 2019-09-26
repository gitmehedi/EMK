# -*- coding: utf-8 -*-
{
    'name': 'Account Asset Vendor Bills',
    'description': """ Create a module for Account Asset Vendor Bills.""",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Extra Tools',
    'depends': [
        'account',
        'account_asset',
        'account_fam',
        'account_category',
        'tds_vendor_bill',
    ],
    'data': [
        'views/asset_vendor_bills_view.xml',
        'views/payment_instrauction_view.xml',
    ],
    'installable': True,
    'application': True,
}
