# -*- coding: utf-8 -*-
{
    'name': 'Account Category',
    'description': """ Main module for asset management which include all css,js and image files.""",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Extra Tools',
    'depends': [
        'account_asset',
        'account_fam',
    ],
    'data': [
        'data/sequence.xml',
        'views/account_asset_category_view.xml',
        'views/account_asset_views.xml',
        'views/product_template_views.xml',
        'views/account_invoice_line_view.xml',
    ],
    'installable': True,
    'application': True,
}
