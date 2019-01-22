# -*- coding: utf-8 -*-
{
    'name': 'Account Fixed Asset Management (FAM)',
    'description': """ Main module for asset management which include all css,js and image files.""",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Extra Tools',
    'depends': [
        'base',
        'operating_unit',
        'account_asset',
        'account',
    ],
    'data': [
        'views/menu_view.xml',
        'views/account_asset_views.xml',
        'views/account_asset_type_view.xml',
        'views/product_template_views.xml',
        'views/account_invoice_line.xml',
        'views/account_move_view.xml',
        'wizard/asset_modify_views.xml',
    ],
    'installable': True,
    'application': True,
}
