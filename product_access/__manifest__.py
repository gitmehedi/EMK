# -*- coding: utf-8 -*-
{
    'name': 'Products Access',
    'description': """ Main module for asset management which include all css,js and image files.""",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'version': '1.0',
    'category': 'Accounting',
    "depends": [
        'account',
        'account_parent',
        'product_users',
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/product_product_view.xml',
    ],
    'installable': True,
    'application': True,
}
