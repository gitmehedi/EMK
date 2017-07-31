# -*- coding: utf-8 -*-

{
    'name': 'Product Extend',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Human Resource',
    'depends': ['base',
                'stock',
                'product',
                'point_of_sale',
                ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml'
    ],
    'summary': 'Test Summary for Extended Product',
    'category': 'Product',
    'summary': 'Product Extend',
    'description': 'Product Extend ',
    'installable': True,
    'application': True,
    'auto_install': False,
}
